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
            'handle_user_enter',
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
        class AcquiringErrorView(LonaView):
            def handle_request(self, request):
                raise exception

        return AcquiringErrorView

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

        # special views
        import_strings = [
            # frontend
            self.server.settings.CORE_FRONTEND_VIEW,
            self.server.settings.FRONTEND_VIEW,

            # erorr 403
            self.server.settings.CORE_ERROR_403_VIEW,
            self.server.settings.ERROR_403_VIEW,

            # erorr 404
            self.server.settings.CORE_ERROR_404_VIEW,
            self.server.settings.ERROR_404_VIEW,

            # erorr 500
            self.server.settings.CORE_ERROR_500_VIEW,
            self.server.settings.ERROR_500_VIEW,
        ]

        for import_string in import_strings:
            if not import_string:
                continue

            # FIXME: run self._run_checks

            view = self._acquire(import_string)
            cache_key = self._gen_cache_key(import_string)
            self._cache[cache_key] = view

    def load(self, view):
        cache_key = self._gen_cache_key(view)

        return self._cache[cache_key]
