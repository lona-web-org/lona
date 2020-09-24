from concurrent.futures import CancelledError
import asyncio
import logging
import os

from aiohttp.web import WebSocketResponse, FileResponse, HTTPFound, Response
from aiohttp import WSMsgType

from lona.view_controller import ViewController
from lona.settings.settings import Settings
from lona.connection import Connection
from lona.scheduling import Scheduler
from lona.routing import Router
from lona.utils import acquire

server_logger = logging.getLogger('lona.server')
static_files_logger = logging.getLogger('lona.server.static_files')
http_logger = logging.getLogger('lona.server.http')
websockets_logger = logging.getLogger('lona.server.websockets')


class LonaServer:
    # TODO: add helper code to load middlewares
    # TODO: add helper code to run middlewares

    def __init__(self, app, project_root, settings_paths=[], loop=None):

        server_logger.debug("starting server in '%s'", project_root)

        self.app = app
        self.project_root = project_root
        self.loop = loop or self.app.loop

        # setup settings
        server_logger.debug('setup settings')

        self.settings = Settings()
        self.settings_paths = ['lona.settings.default_settings']

        project_settings_path = os.path.join(self.project_root, 'settings.py')

        if os.path.exists(project_settings_path):
            self.settings_paths.append('settings.py')

            server_logger.debug("project settings '%s' found",
                                project_settings_path)

        self.settings_paths = self.settings_paths + settings_paths

        for import_string in self.settings_paths:
            server_logger.debug("loading settings from '%s'", import_string)

            self.settings.add(import_string)

        # setup scheduler
        self.scheduler = Scheduler(
            task_zones=self.settings.TASK_ZONES,
            thread_zones=self.settings.THREAD_ZONES,
        )

        self.scheduler.start()

        # setup routing
        server_logger.debug('setup routing')
        self.router = Router()

        server_logger.debug("loading routing table from '%s'",
                            self.settings.ROUTING_TABLE)

        routes = []

        if self.settings.DEBUG:
            routes.extend(acquire('lona.debugger.routes.routes')[1])

        routes.extend(acquire(self.settings.ROUTING_TABLE)[1])

        if routes:
            self.router.add_routes(*routes)

        else:
            server_logger.warning('routing table is empty')

        # setup static files
        server_logger.debug('setup static dirs')

        self.static_dirs = (self.settings.STATIC_DIRS +
                            self.settings.CORE_STATIC_DIRS)

        server_logger.debug('loading static dirs %s',
                            repr(self.static_dirs)[1:-1])

        # setup views
        server_logger.debug('setup views')

        self.view_controller = ViewController(self)

        # setup websocket middlewares
        server_logger.debug('setup websocket middlewares')

        self.websocket_middlewares = (
            self.settings.CORE_WEBSOCKET_MIDDLEWARES +
            self.settings.WEBSOCKET_MIDDLEWARES
        )

        for index, middleware in enumerate(self.websocket_middlewares):
            if callable(middleware):
                continue

            server_logger.debug("loading '%s'", middleware)

            self.websocket_middlewares[index] = acquire(middleware)[1]

        if not self.websocket_middlewares:
            server_logger.debug('no websocket middlewares loaded')

        # setup request middlewares
        server_logger.debug('setup request middlewares')

        self.request_middlewares = [
            *self.settings.REQUEST_MIDDLEWARES,
        ]

        for index, middleware in enumerate(self.request_middlewares):
            if callable(middleware):
                continue

            server_logger.debug("loading '%s'", middleware)

            self.request_middlewares[index] = acquire(middleware)[1]

        if not self.request_middlewares:
            server_logger.debug('no request middlewares loaded')

        # setup aiohttp routes
        server_logger.debug('setup aiohttp routing')

        static_url = self.settings.STATIC_URL_PREFIX + '{path:.*}'

        server_logger.debug('static url set to %s', repr(static_url))

        async def _handle_static_file_request(*args, **kwargs):
            return await self.schedule(
                self.handle_static_file_request,
                *args,
                priority=self.settings.STATIC_REQUEST_PRIORITY,
                **kwargs,
            )

        async def _handle_http_request(*args, **kwargs):
            return await self.schedule(
                self.handle_http_request,
                *args,
                priority=self.settings.HTTP_REQUEST_PRIORITY,
                **kwargs,
            )

        self.app.router.add_route(
            '*', static_url, _handle_static_file_request)

        self.app.router.add_route(
            '*', '/{path_info:.*}', _handle_http_request)

        # finish
        server_logger.debug('setup finish')

    async def shutdown(self, *args, **kwargs):
        server_logger.debug('shutting down')

        await self.schedule(
            self.view_controller.shutdown,
            priority=self.settings.SHUTDOWN_PRIORITY,
        )

        self.scheduler.stop()

    # asyncio helper ##########################################################
    def schedule(self, *args, **kwargs):
        return self.scheduler.schedule(*args, **kwargs)

    # view helper #############################################################
    def render_response(self, response_dict):
        if response_dict['file']:
            return FileResponse(response_dict['file'])

        if response_dict['redirect']:
            return HTTPFound(response_dict['redirect'])

        if response_dict['http_redirect']:
            return HTTPFound(response_dict['http_redirect'])

        return Response(
            status=response_dict['status'],
            content_type=response_dict['content_type'],
            text=response_dict['text'],
        )

    # handle http requests ####################################################
    async def handle_static_file_request(self, request):
        def find_static_file():
            rel_path = request.match_info['path']

            static_files_logger.debug("start search for '%s'", rel_path)

            for static_dir in self.static_dirs[::-1]:
                abs_path = os.path.join(static_dir, rel_path)

                static_files_logger.debug("trying '%s'", abs_path)

                if os.path.exists(abs_path):
                    if os.path.isdir(abs_path):
                        static_files_logger.debug(
                            "'%s' is directory. search stopped", abs_path)

                        return False, ''

                    static_files_logger.debug("returning '%s'", abs_path)

                    return True, abs_path

            static_files_logger.debug("'%s' was not found", rel_path)

            return False, ''

        file_found, abs_path = await self.schedule(
            find_static_file,
            priority=self.settings.STATIC_REQUEST_PRIORITY,
        )

        if file_found:
            return FileResponse(abs_path)

        # TODO: 404 handler
        return Response(
            status=404,
            text='404: Not found',
        )

    async def handle_websocket_message(self, connection, message):
        websockets_logger.debug('%s message received %s', connection, message)

        for middleware in self.websocket_middlewares:
            websockets_logger.debug(
                '%s running websocket middleware %s', connection, middleware)

            try:
                message = await self.schedule(
                    middleware,
                    self,
                    connection,
                    message,
                    priority=self.settings.WEBSOCKET_MIDDLEWARE_PRIORITY,
                )

            except CancelledError:
                # TODO: this happens on shutdown
                # the scheduler should take care of this

                break

            except Exception:
                websockets_logger.error(
                    '%s exception raised while running %s',
                    connection,
                    middleware,
                    exc_info=True,
                )

                break

            if not message:
                # if the middleware does not return the message it is
                # considered as handled

                websockets_logger.debug(
                    '%s message got handled by %s', connection, middleware)

                return

        websockets_logger.debug('%s message got not handled', connection)

    async def handle_websocket_request(self, http_request):
        # setup websocket
        websocket = WebSocketResponse()
        await websocket.prepare(http_request)

        # setup connection
        connection = Connection(self, http_request, websocket)

        websockets_logger.debug('%s opened', connection)

        # main loop
        try:
            async for raw_message in websocket:
                if raw_message.type == WSMsgType.TEXT:
                    self.schedule(
                        self.handle_websocket_message(
                            connection,
                            raw_message.data,
                        ),
                        priority=self.settings.WEBSOCKET_MIDDLEWARE_PRIORITY,
                    )

                elif raw_message.type == WSMsgType.PING:
                    await websocket.pong()

                elif raw_message.type in (WSMsgType.CLOSED, WSMsgType.ERROR):
                    break

        except asyncio.CancelledError:
            websockets_logger.debug('CancelledError')

        finally:
            self.view_controller.remove_connection(connection)

            await websocket.close()

        websockets_logger.debug('%s closed', connection)

        return websocket

    async def handle_http_request(self, http_request):
        # TODO: handle priority overrides by decorators

        http_logger.debug('http request incoming')

        # websocket requests
        if(http_request.method == 'GET' and
           http_request.headers.get('upgrade', '').lower() == 'websocket'):

            return await self.handle_websocket_request(http_request)

        # resolve path
        http_logger.debug('resolving path')

        match, route, match_info = await self.schedule(
            self.router.resolve,
            http_request.path,
            priority=self.settings.ROUTING_PRIORITY,
        )

        if match:
            http_logger.debug('route %s matched', route)

            # http pass through
            if route.http_pass_through:
                http_logger.debug('http_pass_through mode')

                if asyncio.iscoroutinefunction(route.handler):
                    response = await route.handler(http_request)

                else:
                    response = await self.schedule(
                        route.handler,
                        http_request,
                        priority=self.settings.DEFAULT_VIEW_PRIORITY,
                    )

                # FIXME: wsgi container
                if asyncio.iscoroutine(response):
                    response = await response

                # render and return response
                if isinstance(response, Response):
                    return response

                return await self.schedule(
                    self.render_response,
                    response,
                    priority=self.settings.DEFAULT_VIEW_PRIORITY,
                )

            connection = Connection(self, http_request)

            # non interactive views
            if not route.interactive:
                http_logger.debug('non-interactive mode')

                post_data = await http_request.post()

                response_dict = await self.schedule(
                    self.view_controller.run_view_non_interactive,
                    url=http_request.path,
                    connection=connection,
                    route=route,
                    match_info=match_info,
                    frontend=False,
                    post_data=post_data,
                    priority=self.settings.DEFAULT_VIEW_PRIORITY,
                )

                return self.render_response(response_dict)

        # frontend views
        http_logger.debug('frontend mode')

        post_data = await http_request.post()

        response_dict = await self.schedule(
            self.view_controller.run_view_non_interactive,
            url=http_request.path,
            connection=connection,
            route=route,
            match_info=match_info,
            frontend=True,
            post_data=post_data,
            priority=self.settings.DEFAULT_VIEW_PRIORITY,
        )

        return self.render_response(response_dict)
