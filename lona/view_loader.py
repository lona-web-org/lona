import asyncio
import inspect
import logging

logger = logging.getLogger('lona.view_loader')


class ViewSpec:
    def __init__(self, view, route=None):
        self.view = view
        self.route = route

        self.multi_user = getattr(self.view, 'multi_user', False)
        self.is_class_based = False
        self.has_input_event_root_handler = False
        self.has_input_event_handler = False

        if inspect.isclass(self.view):
            self.is_class_based = True

            self.has_input_event_root_handler = hasattr(
                self.view, 'handle_input_event_root')

            self.has_input_event_handler = hasattr(
                self.view, 'handle_input_event')

        # check callbacks
        # handle_request
        handle_request = None

        if self.is_class_based:
            if not hasattr(self.view, 'handle_request'):
                logger.error("%s has no attribute 'handle_request'", self.view)

            else:
                handle_request = self.view.handle_request

        else:
            handle_request = self.view

        if not self.route or not self.route.http_pass_through:
            # if a view talks to the aiohttp directly through http pass
            # through mode, coroutines have to be allowed

            if asyncio.iscoroutinefunction(handle_request):
                logger.error('%s is a coroutine function', handle_request)

            # handle_input_event_root
            if(self.has_input_event_root_handler and
               asyncio.iscoroutinefunction(self.view.handle_input_event_root)):

                logger.error(
                    '%s is a coroutine function',
                    self.view.handle_input_event_root,
                )

            # handle_input_event
            if(self.has_input_event_handler and
               asyncio.iscoroutinefunction(self.view.handle_input_event)):

                logger.error(
                    '%s is a coroutine function',
                    self.view.handle_input_event,
                )


class ViewLoader:
    def __init__(self, server):
        self.server = server

        self.setup()

    def _gen_cache_key(self, view):
        try:
            hash(view)

            return view

        except TypeError:
            return id(view)

    def _generate_acquiring_error_view(self, exception):
        def view(request):
            raise exception

        return view

    def _acquire(self, view):
        logger.debug('loading %s', view)

        if isinstance(view, str):
            try:
                view = self.server.acquire(view)

            except Exception as exception:
                logger.error(
                    "exception raised while importing '%s'",
                    view,
                    exc_info=True,
                )

                view = self._generate_acquiring_error_view(exception)

        return view

    def _handle_404(self, request):
        try:
            return self._error_404_handler(request)

        except Exception:
            logger.error(
                'Exception occurred while running %s. Falling back to %s',
                self._error_404_handler,
                self._error_404_fallback_handler,
                exc_info=True,
            )

        return self._error_404_fallback_handler(request)

    def _handle_500(self, request, exception):
        try:
            return self._error_500_handler(request, exception)

        except Exception:
            logger.error(
                'Exception occurred while running %s. Falling back to %s',
                self._error_500_handler,
                self._error_500_fallback_handler,
                exc_info=True,
            )

        return self._error_500_fallback_handler(request, exception)

    def setup(self):
        # views
        logger.debug('loading views from routes')

        self._cache = {}

        for route in self.server.router.routes:
            view = self._acquire(route.view)
            cache_key = self._gen_cache_key(route.view)
            view_spec = ViewSpec(view, route=route)
            self._cache[cache_key] = (view_spec, view)

            if route.frontend_view:
                view = self._acquire(route.frontend_view)
                cache_key = self._gen_cache_key(route.frontend_view)
                view_spec = ViewSpec(view)
                self._cache[cache_key] = (view_spec, view)

        # frontend view
        frontend_view = self._acquire(self.server.settings.FRONTEND_VIEW)
        frontend_view_spec = ViewSpec(frontend_view)

        cache_key = self._gen_cache_key(self.server.settings.FRONTEND_VIEW)
        self._cache[cache_key] = (frontend_view_spec, frontend_view)

        # 404 handler
        self._error_404_handler = self._acquire(
            self.server.settings.ERROR_404_HANDLER,
        )

        self._error_404_fallback_handler = self._acquire(
            self.server.settings.ERROR_404_FALLBACK_HANDLER,
        )

        cache_key = self._gen_cache_key(self.server.settings.ERROR_404_HANDLER)
        view_spec = ViewSpec(self._error_404_handler)
        self._cache[cache_key] = (view_spec, self._handle_404)

        if view_spec.is_class_based:
            logger.error('404 handler should be simple callback')

        # 500 handler
        self._error_500_handler = self._acquire(
            self.server.settings.ERROR_500_HANDLER,
        )

        self._error_500_fallback_handler = self._acquire(
            self.server.settings.ERROR_500_FALLBACK_HANDLER,
        )

        cache_key = self._gen_cache_key(self.server.settings.ERROR_500_HANDLER)
        view_spec = ViewSpec(self._error_500_handler)
        self._cache[cache_key] = (view_spec, self._handle_500)

        if view_spec.is_class_based:
            logger.error('500 handler should be simple callback')

    def load(self, view):
        cache_key = self._gen_cache_key(view)

        return self._cache[cache_key]
