import asyncio
import logging
import inspect

from lona.view import LonaView

logger = logging.getLogger('lona.view_loader')


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

    def _run_checks(self, route, view):
        # check if view is instance of lona.views.LonaView
        if(not route.http_pass_through and
           (not inspect.isclass(view) or not issubclass(view, LonaView))):

            logger.error('%s is no lona view', route.view)

            return

        # check if lona specific hooks are coroutine functions
        hook_names = [
            'handle_request',
            'handle_input_event_root',
            'handle_input_event',
        ]

        for hook_name in hook_names:
            hook = getattr(view, hook_name, None)

            if(not route.http_pass_through and
               asyncio.iscoroutinefunction(hook)):

                logger.error(
                    '%s.%s is a coroutine function',
                    route.view,
                    hook_name,
                )

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

    def _run_error_403_view(self, request):
        try:
            view = self._error_403_view()

            return view.handle_request(request)

        except Exception:
            logger.error(
                'Exception occurred while running %s. Falling back to %s',
                self._error_403_view,
                self._error_403_fallback_view,
                exc_info=True,
            )

        view = self._error_403_fallback_view()

        return view.handle_request(request)

    def _run_error_404_view(self, request):
        try:
            view = self._error_404_view()

            return view.handle_request(request)

        except Exception:
            logger.error(
                'Exception occurred while running %s. Falling back to %s',
                self._error_404_view,
                self._error_404_fallback_view,
                exc_info=True,
            )

        view = self._error_404_fallback_view()

        return view.handle_request(request)

    def _run_error_500_view(self, request, exception):
        try:
            view = self._error_500_view()

            return view.handle_request(request, exception)

        except Exception:
            logger.error(
                'Exception occurred while running %s. Falling back to %s',
                self._error_500_view,
                self._error_500_fallback_view,
                exc_info=True,
            )

        view = self._error_500_fallback_view()

        return view.handle_request(request, exception)

    def setup(self):
        # views
        logger.debug('loading views from routes')

        self._cache = {}

        for route in self.server.router.routes:
            view = self._acquire(route.view)

            self._run_checks(route, view)

            cache_key = self._gen_cache_key(route.view)
            self._cache[cache_key] = view

            if route.frontend_view:
                view = self._acquire(route.frontend_view)
                cache_key = self._gen_cache_key(route.frontend_view)
                self._cache[cache_key] = view

        # frontend view
        frontend_view = self._acquire(self.server.settings.FRONTEND_VIEW)

        cache_key = self._gen_cache_key(self.server.settings.FRONTEND_VIEW)
        self._cache[cache_key] = frontend_view

        # error 403 view
        self._error_403_view = self._acquire(
            self.server.settings.ERROR_403_VIEW,
        )

        self._error_403_fallback_view = self._acquire(
            self.server.settings.ERROR_403_FALLBACK_VIEW,
        )

        cache_key = self._gen_cache_key(self.server.settings.ERROR_403_VIEW)
        self._cache[cache_key] = self._run_error_403_view

        # error 404 view
        self._error_404_view = self._acquire(
            self.server.settings.ERROR_404_VIEW,
        )

        self._error_404_fallback_view = self._acquire(
            self.server.settings.ERROR_404_FALLBACK_VIEW,
        )

        cache_key = self._gen_cache_key(self.server.settings.ERROR_404_VIEW)
        self._cache[cache_key] = self._run_error_404_view

        # error 500 view
        self._error_500_view = self._acquire(
            self.server.settings.ERROR_500_VIEW,
        )

        self._error_500_fallback_view = self._acquire(
            self.server.settings.ERROR_500_FALLBACK_VIEW,
        )

        cache_key = self._gen_cache_key(self.server.settings.ERROR_500_VIEW)
        self._cache[cache_key] = self._run_error_500_view

    def load(self, view):
        cache_key = self._gen_cache_key(view)

        return self._cache[cache_key]
