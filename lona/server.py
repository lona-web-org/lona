from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging
import os

from aiohttp.web import WebSocketResponse, FileResponse, HTTPFound, Response
from aiohttp import WSMsgType

from lona.view_runtime_controller import ViewRuntimeController
from lona.middleware_controller import MiddlewareController
from lona.static_files import StaticFileLoader
from lona.templating import TemplatingEngine
from lona.settings.settings import Settings
from lona.server_state import ServerState
from lona.view_runtime import ViewRuntime
from lona.view_loader import ViewLoader
from lona.connection import Connection
from lona.imports import acquire
from lona.routing import Router
from lona.types import Mapping

DEFAULT_SETTINGS_PRE = os.path.join(
    os.path.dirname(__file__),
    'settings/default_settings_pre.py',
)

DEFAULT_SETTINGS_POST = os.path.join(
    os.path.dirname(__file__),
    'settings/default_settings_post.py',
)

server_logger = logging.getLogger('lona.server')
http_logger = logging.getLogger('lona.server.http')
websockets_logger = logging.getLogger('lona.server.websockets')


class LonaServer:
    def __init__(self, app, project_root, settings_paths=[],
                 settings_pre_overrides={}, settings_post_overrides={},
                 loop=None):

        server_logger.debug("starting server in '%s'", project_root)

        self.app = app
        self.project_root = project_root
        self.loop = loop or self.app.loop

        self.websocket_connections = []
        self.user = Mapping()

        # setup settings
        server_logger.debug('setup settings')

        self.settings_paths = [
            DEFAULT_SETTINGS_PRE,
            *settings_paths,
            DEFAULT_SETTINGS_POST,
        ]

        self.settings = Settings()

        if settings_pre_overrides:
            server_logger.debug('applying settings pre overrides')

            self.settings.update(settings_pre_overrides)

        for import_string in self.settings_paths:
            server_logger.debug("loading settings from '%s'", import_string)

            self.settings.add(import_string)

        if settings_post_overrides:
            server_logger.debug('applying settings post overrides')

            self.settings.update(settings_post_overrides)

        # setup threads
        self.executor = ThreadPoolExecutor(
            max_workers=self.settings.MAX_WORKERS,
        )

        # setup server state
        server_logger.debug('setup server state')

        if self.settings.SERVER_STATE_ATOMIC:
            self._state = ServerState(initial_data={})

        else:
            self._state = {}

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

        # setup templating
        server_logger.debug('setup templating')

        self.templating_engine = TemplatingEngine(self)

        # setup websocket middleware controller
        server_logger.debug('setup middleware controller')

        self.middleware_controller = MiddlewareController(self)

        # setup aiohttp routes
        server_logger.debug('setup aiohttp routing')

        static_url = self.settings.STATIC_URL_PREFIX + '{path:.*}'

        server_logger.debug('static url set to %s', repr(static_url))

        self.app.router.add_route(
            '*', static_url, self._handle_static_file_request)

        self.app.router.add_route(
            '*', '/{path_info:.*}', self._handle_http_request)

        # setup view loader
        server_logger.debug('setup view loader')

        self.view_loader = ViewLoader(self)

        # setup views
        server_logger.debug('setup view runtime controller')

        self.view_runtime_controller = ViewRuntimeController(self)
        self.view_runtime_controller.start()

        # setup static files
        # the static file loader has to be started last because it does
        # node class discovery which has to happen after all views are imported
        server_logger.debug('setup static file')

        self.static_file_loader = StaticFileLoader(self)

        # setup startup hooks
        server_logger.debug('setup startup hooks')

        for hook in self.settings.STARTUP_HOOKS:
            if isinstance(hook, str):
                try:
                    hook = acquire(hook)[1]

                except Exception:
                    server_logger.error(
                        "Exception occurred while importing startup hook '%s'",
                        hook,
                        exc_info=True,
                    )

                    continue

            self.app.on_startup.append(hook)

        # setup shutdown hooks
        server_logger.debug('setup shutdown hooks')

        for hook in self.settings.SHUTDOWN_HOOKS:
            if isinstance(hook, str):
                try:
                    hook = acquire(hook)[1]

                except Exception:
                    server_logger.error(
                        "Exception occurred while importing shutdown hook '%s'",  # NOQA
                        hook,
                        exc_info=True,
                    )

                    continue

            self.app.on_shutdown.append(hook)

        # finish
        server_logger.debug('setup finish')

    async def stop(self, *args, **kwargs):
        server_logger.debug('shutting down')

        await self.run_function_async(self.view_runtime_controller.stop)
        await self.loop.run_in_executor(None, self.executor.shutdown)

    # asyncio helper ##########################################################
    def run_coroutine_sync(self, coroutine, wait=True):
        future = asyncio.run_coroutine_threadsafe(coroutine, loop=self.loop)

        if wait:
            return future.result()

        return future

    def run_function_async(self, function, *args, **kwargs):
        def _function():
            return function(*args, **kwargs)

        return self.loop.run_in_executor(self.executor, _function)

    def run(self, function_or_coroutine,
            *args, sync=False, wait=True, **kwargs):

        is_coroutine = asyncio.iscoroutine(function_or_coroutine)

        is_coroutine_function = asyncio.iscoroutinefunction(
            function_or_coroutine)

        # coroutine
        if is_coroutine or is_coroutine_function:
            coroutine = function_or_coroutine

            if is_coroutine_function:
                coroutine = function_or_coroutine(*args, **kwargs)

            # sync
            if sync:
                return self.run_coroutine_sync(coroutine, wait=wait)

            # async
            else:
                return coroutine

        # function
        else:
            function = function_or_coroutine

            def _function():
                return function(*args, **kwargs)

            # sync
            if sync:
                if wait:
                    return function(*args, **kwargs)

                return self.loop.run_in_executor(self.executor, _function)

            # async
            else:
                return self.run_function_async(function, *args, **kwargs)

    # connection management ###################################################
    async def _setup_connection(self, http_request, websocket=None):
        connection = Connection(self, http_request, websocket)

        handled, data, middleware = \
            await self.middleware_controller.process_connection(
                connection,
            )

        if websocket is not None:
            self.websocket_connections.append(connection)

            if connection.user not in self.user:
                self.user[connection.user] = []

            self.user[connection.user].append(connection)

        return connection, (handled, data, middleware)

    def _remove_connection(self, connection):
        if connection in self.websocket_connections:
            self.websocket_connections.remove(connection)

        if connection.user in self.user:
            self.user[connection.user].remove(connection)

            if len(self.user[connection.user]) == 0:
                self.user.pop(connection.user)

    # view helper #############################################################
    def _render_response(self, response_dict):
        if response_dict['file']:
            return FileResponse(response_dict['file'])

        if response_dict['redirect']:
            return HTTPFound(response_dict['redirect'])

        if response_dict['http_redirect']:
            return HTTPFound(response_dict['http_redirect'])

        response = Response(
            status=response_dict['status'],
            content_type=response_dict['content_type'],
            text=response_dict['text'],
        )

        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # NOQA

        return response

    # handle http requests ####################################################
    async def _handle_static_file_request(self, request):
        rel_path = request.match_info['path']

        abs_path = await self.run_function_async(
            self.static_file_loader.resolve_path,
            rel_path,
        )

        if not abs_path:
            return Response(
                status=404,
                text='404: Not found',
            )

        return FileResponse(abs_path)

    async def _handle_websocket_message(self, connection, message):
        websockets_logger.debug(
            '%s message received %s', connection, message.data)

        handled, data, middleware = \
            await self.middleware_controller.process_websocket_message(
                connection,
                message.data,
            )

        if not handled:
            websockets_logger.debug(
                '%s message got not handled', connection)

    async def _handle_websocket_request(self, http_request):
        websocket = None
        connection = None

        async def close_websocket():
            self.view_runtime_controller.remove_connection(connection)
            self._remove_connection(connection)

            await websocket.close()

            websockets_logger.debug('%s closed', connection)

        # setup websocket
        websocket = WebSocketResponse()
        await websocket.prepare(http_request)

        # setup connection
        connection, middleware_data = await self._setup_connection(
            http_request,
            websocket,
        )

        handled, data, middleware = middleware_data

        # connection got closed by middleware
        if handled:
            if data:
                if not isinstance(data, str):
                    raise RuntimeError('%s.process_connection returned non string data'.format(middleware))  # NOQA

                await connection.send_str(data, sync=False)

            await close_websocket()

            return websocket

        websockets_logger.debug('%s opened', connection)

        # main loop
        try:
            async for message in websocket:
                if message.type == WSMsgType.TEXT:
                    self.loop.create_task(
                        self._handle_websocket_message(connection, message),
                    )

                elif message.type == WSMsgType.PING:
                    await websocket.pong()

                elif message.type in (WSMsgType.CLOSED, WSMsgType.ERROR):
                    break

        except asyncio.CancelledError:
            websockets_logger.debug('CancelledError')

        finally:
            await close_websocket()

        return websocket

    async def _handle_http_request(self, http_request):
        http_logger.debug('http request incoming')

        # resolve path
        http_logger.debug("resolving path %s", repr(http_request.path))

        match, route, match_info = await self.run_function_async(
            self.router.resolve,
            http_request.path,
        )

        if match:
            http_logger.debug('route %s matched', route)

        else:
            http_logger.debug('no route matched')

        # http pass through
        if match and route.http_pass_through:
            http_logger.debug('http_pass_through mode')

            # load view
            if isinstance(route.view, str):
                view = await self.run_function_async(
                    self.view_loader.load,
                    route.view,
                )

            else:
                view = route.view

            # run view
            if asyncio.iscoroutinefunction(view):
                response = await view(http_request)

            else:
                response = await self.run_function_async(
                    view,
                    http_request,
                )

            if asyncio.iscoroutine(response):
                response = await response

            # render and return response
            if isinstance(response, Response):
                return response

            return await self.run_function_async(
                self._render_response,
                response,
            )

        # websocket requests
        if(http_request.method == 'GET' and
           http_request.headers.get('upgrade', '').lower() == 'websocket'):

            return await self._handle_websocket_request(http_request)

        # setup connection
        try:
            connection, middleware_data = await self._setup_connection(
                http_request,
            )

        except Exception:
            http_logger.error(
                'Exception occurred while setting connection up',
                exc_info=True,
            )

            return Response(status=500, body='500: Internal Error')

        handled, data, middleware = middleware_data

        # connection got closed by middleware
        if handled:
            if data:
                return self._render_response(data)

            return Response(status=503, body='503: Service Unavailable')

        # run non interactive view or frontend
        if match and not route.interactive:
            frontend = False

            http_logger.debug('non-interactive mode')

        else:
            http_logger.debug('frontend mode')

            frontend = True

        view_runtime = ViewRuntime(
            server=self,
            url=http_request.path,
            route=route,
            match_info=match_info,
            post_data=await http_request.post(),
            frontend=frontend,
            start_connection=connection,
        )

        response_dict = await self.run_function_async(
            view_runtime.run_middlewares,
        )

        if not response_dict:
            response_dict = await self.run_function_async(
                view_runtime.start,
            )

        return self._render_response(response_dict)

    # state ###################################################################
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, data):
        if self.settings.SERVER_STATE_ATOMIC:
            self._state._reset(data)

        else:
            self._state = data

    # helper ##################################################################
    def get_running_views_count(self, *args, **kwargs):
        return self.view_runtime_controller.get_running_views_count(
            *args,
            **kwargs,
        )

    def get_connection_count(self, user):
        if user not in self.user:
            return 0

        return len(self.user[user])

    def get_template(self, *args, **kwargs):
        return self.templating_engine.get_template(*args, **kwargs)

    def render_string(self, *args, **kwargs):
        return self.templating_engine.render_string(*args, **kwargs)

    def render_template(self, *args, **kwargs):
        return self.templating_engine.render_template(*args, **kwargs)

    def reverse(self, *args, **kwargs):
        return self.router.reverse(*args, **kwargs)
