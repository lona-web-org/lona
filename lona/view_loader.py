from __future__ import annotations

from typing import Type, cast
import logging
import inspect
import asyncio

from lona.routing import Route
from lona.view import View

logger = logging.getLogger('lona.view_loader')


class ViewLoader:
    # FIXME: type annotations: views can also be callbacks to make
    # aiohttp-wsgi work

    def __init__(self, server):
        self.server = server

        self.setup()

    def _gen_cache_key(
            self,
            view: type[View] | str,
    ) -> type[View] | str | int:

        try:
            hash(view)

            return view

        except TypeError:
            return id(view)

    def _run_checks(self, route: Route, view: type[View]) -> None:
        # check if view is instance of lona.views.View
        if (not route.http_pass_through and
                (not inspect.isclass(view) or not issubclass(view, View))):

            logger.error('%s is no lona view', route.view)

            return

        # check if lona specific hooks are coroutine functions
        hook_names = [
            'handle_request',
            'handle_input_event_root',
            'handle_input_event',
            'on_view_event',
            'on_stop',
            'on_cleanup',
        ]

        for hook_name in hook_names:
            hook = getattr(view, hook_name, None)

            if (not route.http_pass_through and
                    asyncio.iscoroutinefunction(hook)):

                logger.error(
                    '%s.%s is a coroutine function',
                    route.view,
                    hook_name,
                )

    def _generate_acquiring_error_view(
            self,
            exception: Exception,
    ) -> type[View]:

        class AcquiringErrorView(View):
            def handle_request(self, request):
                raise exception

        return AcquiringErrorView

    def _acquire(self, view: type[View] | str) -> type[View]:
        logger.debug('loading %s', view)

        if isinstance(view, str):
            try:
                view = self.server.acquire(view)

            except Exception as exception:
                logger.exception("exception raised while importing '%s'", view)

                view = self._generate_acquiring_error_view(exception)

        return cast('type[View]', view)

    def _cache_view(
            self,
            route: Route | None,
            view: type[View] | str,
    ) -> None:

        view_class = self._acquire(view)

        if route:
            self._run_checks(route, view_class)

        cache_key = self._gen_cache_key(view)
        self._cache[cache_key] = view_class

    def setup(self):
        # views
        logger.debug('loading views from routes')

        self._cache = {}

        for route in self.server._router.routes:
            self._cache_view(
                route=route,
                view=route.view,
            )

            if route.frontend_view:
                self._cache_view(
                    route=None,
                    view=route.frontend_view,
                )

        # special views
        import_strings = [
            # frontend
            self.server.settings.CORE_FRONTEND_VIEW,
            self.server.settings.FRONTEND_VIEW,

            # error 403
            self.server.settings.CORE_ERROR_403_VIEW,
            self.server.settings.ERROR_403_VIEW,

            # error 404
            self.server.settings.CORE_ERROR_404_VIEW,
            self.server.settings.ERROR_404_VIEW,

            # error 500
            self.server.settings.CORE_ERROR_500_VIEW,
            self.server.settings.ERROR_500_VIEW,
        ]

        for import_string in import_strings:
            if not import_string:
                continue

            self._cache_view(
                route=None,
                view=import_string,
            )

    def load(self, view: type[View] | str) -> type[View]:
        cache_key = self._gen_cache_key(view)

        return cast(Type[View], self._cache[cache_key])

    def get_all_views(self) -> list[type[View]]:
        return list(self._cache.values())
