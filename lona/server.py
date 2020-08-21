from concurrent.futures import CancelledError
from functools import partial
import asyncio
import logging
import os

from aiohttp.web import WebSocketResponse, FileResponse, HTTPFound, Response
from aiohttp import WSMsgType

from lona.view_controller import ViewController
from lona.settings.settings import Settings
from lona.connection import Connection
from lona.routing import Router
from lona.utils import acquire

server_logger = logging.getLogger('lona.server')
static_files_logger = logging.getLogger('lona.server.static_files')
http_logger = logging.getLogger('lona.server.http')
websockets_logger = logging.getLogger('lona.server.websockets')


class LonaServer:
    def __init__(self, app, project_root, settings_paths=[], loop=None,
                 executor=None):

        server_logger.debug("starting server in '%s'", project_root)

        self.app = app
        self.project_root = project_root
        self.executor = executor
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

        # setup aiohttp routes
        server_logger.debug('setup aiohttp routing')

        static_url = self.settings.STATIC_URL_PREFIX + '{path:.*}'

        server_logger.debug('static url set to %s', repr(static_url))

        self.app.router.add_route(
            '*', static_url, self.handle_static_file_request)

        self.app.router.add_route(
            '*', '/{path_info:.*}', self.handle_http_request)

        # finish
        server_logger.debug('setup finish')

    async def shutdown(self, *args, **kwargs):
        server_logger.debug('shutting down')

        await self.run_function_async(
            self.view_controller.shutdown)

    # asyncio helper ##########################################################
    async def run_function_async(self, function, *args, **kwargs):
        if not isinstance(function, partial):
            function = partial(function, *args, **kwargs)

        return await self.loop.run_in_executor(self.executor, function)

    def run_coroutine_sync(self, coroutine, wait=True):
        future = asyncio.run_coroutine_threadsafe(coroutine, loop=self.loop)

        if wait:
            return future.result()

        return future

    async def run_threadsafe(self, function, *args, **kwargs):
        if asyncio.iscoroutine(function):
            return await function

        if asyncio.iscoroutinefunction(function):
            return await function(*args, **kwargs)

        return await self.run_function_async(function, *args, **kwargs)

    # view helper #############################################################
    def render_response(self, response_dict):
        if response_dict['file']:
            return FileResponse(response_dict['file'])

        if response_dict['redirect']:
            return HTTPFound(response_dict['redirect'])

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

        file_found, abs_path = await self.run_function_async(find_static_file)

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
                message = await self.run_threadsafe(
                    middleware,
                    self,
                    connection,
                    message,
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

                    # TODO: scheduling
                    self.loop.create_task(
                        self.handle_websocket_message(
                            connection,
                            raw_message.data,
                        )
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
        http_logger.debug('http request incoming')

        # websocket requests
        if(http_request.method == 'GET' and
           http_request.headers.get('upgrade', '').lower() == 'websocket'):

            return await self.handle_websocket_request(http_request)

        # resolve path
        http_logger.debug('resolving path')

        match, route, match_info = await self.run_function_async(
            self.router.resolve, http_request.path)

        if match:
            http_logger.debug('route %s matched', route)

            # http pass through
            if route.http_pass_through:
                http_logger.debug('http_pass_through mode')

                if asyncio.iscoroutinefunction(route.handler):
                    response = await route.handler(http_request)

                else:
                    response = await self.run_function_async(
                        route.handler, http_request)

                # FIXME: wsgi container
                if asyncio.iscoroutine(response):
                    response = await response

                # render and return response
                if isinstance(response, Response):
                    return response

                return await self.run_function_async(
                    self.render_response, response)

            # non interactive views
            if not route.interactive:
                http_logger.debug('non-interactive mode')

                def run_view(post_data):
                    view = self.view_controller.get_view(
                        url=http_request.path,
                        route=route,
                        match_info=match_info,
                    )

                    response_dict = view.run(post_data=post_data)

                    return self.render_response(response_dict)

                post_data = await http_request.post()
                response = await self.run_function_async(run_view, post_data)

                return response

        # frontend views
        http_logger.debug('frontend mode')

        def frontend(post_data):
            view = self.view_controller.get_view(
                url=http_request.path,
                route=route,
                match_info=match_info,
                frontend=True,
            )

            response_dict = view.run(post_data=post_data)

            return self.render_response(response_dict)

        post_data = await http_request.post()
        response = await self.run_function_async(frontend, post_data)

        return response
