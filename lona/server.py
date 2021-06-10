import asyncio
import logging
import inspect
import os

from aiohttp import WSMsgType

from aiohttp.web import (
    WebSocketResponse,
    FileResponse,
    HTTPFound,
    Response,
)

from lona.view_runtime_controller import ViewRuntimeController
from lona.middleware_controller import MiddlewareController
from lona.client_pre_compiler import ClientPreCompiler
from lona.static_file_loader import StaticFileLoader
from lona.message_bus.broker import MessageBusBroker
from lona.message_bus.client import MessageBusClient
from lona.response_parser import ResponseParser
from lona.templating import TemplatingEngine
from lona.imports import acquire as _acquire
from lona.server_state import ServerState
from lona.view_runtime import ViewRuntime
from lona.view_loader import ViewLoader
from lona.connection import Connection
from lona.settings import Settings
from lona.routing import Router
from lona.types import Mapping

DEFAULT_SETTINGS = os.path.join(
    os.path.dirname(__file__),
    'default_settings.py',
)

server_logger = logging.getLogger('lona.server')
http_logger = logging.getLogger('lona.server.http')
websockets_logger = logging.getLogger('lona.server.websockets')


class LonaServer:
    def __init__(self, app, project_root, settings_paths=[],
                 settings_pre_overrides={}, settings_post_overrides={},
                 message_broker_mode=False,
                 host='', port=None):

        self.project_root = os.path.abspath(project_root)
        self.message_broker_mode = message_broker_mode
        self.host = host
        self.port = port

        self.websocket_connections = []
        self.user = Mapping()
        self._loop = None
        self._worker_pool = None
        self.hostname = os.uname().nodename

        server_logger.debug("starting server in '%s'", project_root)

        if self.message_broker_mode:
            server_logger.debug('running in message broker mode')

        # setup aiohttp app
        self._app = app
        self._app['lona_server'] = self

        self._app.on_startup.append(self.start)
        self._app.on_shutdown.append(self.stop)

        # setup settings
        server_logger.debug('setup settings')

        self.settings_paths = [
            DEFAULT_SETTINGS,
        ]

        for path in settings_paths:
            self.settings_paths.append(
                os.path.normpath(
                    os.path.join(self.project_root, path),
                )
            )

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

        # setup templating
        server_logger.debug('setup templating')

        self.templating_engine = TemplatingEngine(self)

        # setup message bus
        server_logger.debug('setup message bus')

        self.message_bus_broker = MessageBusBroker(server=self)
        self.message_bus_client = MessageBusClient(server=self)

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

        routes = self.acquire(self.settings.ROUTING_TABLE)

        if routes:
            self.router.add_routes(*routes)

        else:
            server_logger.warning('routing table is empty')

        # setup websocket middleware controller
        server_logger.debug('setup middleware controller')

        self.middleware_controller = MiddlewareController(self)

        # setup aiohttp routes
        server_logger.debug('setup aiohttp routing')

        if self.message_broker_mode or self.settings.MESSAGE_BROKER:
            self._app.router.add_route(
                '*',
                self.settings.MESSAGE_BROKER_URL,
                self.message_bus_broker.handle_http_request,
            )

        if not self.message_broker_mode:
            static_url = self.settings.STATIC_URL_PREFIX + '{path:.*}'

            server_logger.debug('static url set to %s', repr(static_url))

            self._app.router.add_route(
                '*', static_url, self._handle_static_file_request)

            self._app.router.add_route(
                '*', '/{path_info:.*}', self._handle_http_request)

        # setup view loader
        server_logger.debug('setup view loader')

        self.view_loader = ViewLoader(self)

        # setup response parser
        server_logger.debug('setup response parser')

        self.response_parser = ResponseParser(self)

        # setup views
        server_logger.debug('setup view runtime controller')

        self.view_runtime_controller = ViewRuntimeController(self)

        # setup static files
        self.client_pre_compiler = ClientPreCompiler(self)

        # the static file loader has to be started last because it does
        # node class discovery which has to happen after all views are imported
        server_logger.debug('setup static file')

        self.static_file_loader = StaticFileLoader(self)

        # setup startup hooks
        server_logger.debug('setup startup hooks')

        for hook in self.settings.STARTUP_HOOKS:
            if isinstance(hook, str):
                try:
                    hook = self.acquire(hook)

                except Exception:
                    server_logger.error(
                        "Exception occurred while importing startup hook '%s'",
                        hook,
                        exc_info=True,
                    )

                    continue

            self._app.on_startup.append(hook)

        # setup shutdown hooks
        server_logger.debug('setup shutdown hooks')

        for hook in self.settings.SHUTDOWN_HOOKS:
            if isinstance(hook, str):
                try:
                    hook = self.acquire(hook)

                except Exception:
                    server_logger.error(
                        "Exception occurred while importing shutdown hook '%s'",  # NOQA
                        hook,
                        exc_info=True,
                    )

                    continue

            self._app.on_shutdown.append(hook)

        # finish
        server_logger.debug('setup finish')

    def set_loop(self, loop):
        self._loop = loop

    def set_worker_pool(self, worker_pool):
        self._worker_pool = worker_pool

    @property
    def loop(self):
        return self._loop

    @property
    def worker_pool(self):
        return self._worker_pool

    async def start(self, *args, **kwargs):
        server_logger.debug('start')

        if not self._loop:
            raise RuntimeError('loop is not set')

        if not self._worker_pool:
            raise RuntimeError('worker_pool is not set')

        # run checks
        # tests
        test_names = [
            'TEST_VIEW_START_TIMEOUT',
            'TEST_INPUT_EVENT_TIMEOUT',
        ]

        for test_name in test_names:
            if self.settings.get(test_name, False):
                server_logger.warning('%s is enabled', test_name)

        self.view_runtime_controller.start()
        await self.message_bus_client.start()

    async def stop(self, *args, **kwargs):
        server_logger.debug('stop')

        await self.run_function_async(self.view_runtime_controller.stop)
        await self.message_bus_broker.stop()
        await self.message_bus_client.stop()

        for connection in self.websocket_connections.copy():
            try:
                await connection.websocket.close()

            except Exception:
                pass

    # asyncio helper ##########################################################
    def run_coroutine_sync(self, coroutine, wait=True):
        future = asyncio.run_coroutine_threadsafe(coroutine, loop=self._loop)

        if wait:
            return future.result()

        return future

    def run_function_async(self, function, *args,
                           excutor_name='worker', **kwargs):

        def _function():
            return function(*args, **kwargs)

        return self._loop.run_in_executor(
            self._worker_pool.get_executor(excutor_name),
            _function,
        )

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

                return self._loop.run_in_executor(self._executor, _function)

            # async
            else:
                return self.run_function_async(function, *args, **kwargs)

    # path helper #############################################################
    def resolve_path(self, path):
        if path.startswith('/'):
            return path

        return os.path.normpath(os.path.join(self.project_root, path))

    def acquire(self, import_string, *args, **kwargs):
        if '::' in import_string:
            script, attribute_name = import_string.split('::')
            script = self.resolve_path(script)

            import_string = '{}::{}'.format(script, attribute_name)

        return _acquire(import_string, *args, **kwargs)

    # connection management ###################################################
    async def _setup_connection(self, http_request, websocket=None):
        connection = Connection(self, http_request, websocket)

        handled, data, middleware = \
            await self.middleware_controller.handle_connection(
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
        def _404():
            return Response(
                status=404,
                text='404: Not found',
            )

        if not self.settings.STATIC_FILES_SERVE:
            server_logger.warning(
                'Reverse proxy seems to be misconfigured: a static file request was received but STATIC_FILES_SERVE is disabled',  # NOQA
            )

            return _404()

        rel_path = request.match_info['path']

        abs_path = await self.run_function_async(
            self.static_file_loader.resolve_path,
            rel_path,
            excutor_name='static_worker',
        )

        if not abs_path:
            return _404()

        return FileResponse(abs_path)

    async def _handle_websocket_message(self, connection, message):
        websockets_logger.debug(
            '%s message received %s', connection, message.data)

        handled, data, middleware = \
            await self.middleware_controller.handle_websocket_message(
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
                    raise RuntimeError('%s.handle_connection returned non string data'.format(middleware))  # NOQA

                await connection.send_str(data, sync=False)

            await close_websocket()

            return websocket

        websockets_logger.debug('%s opened', connection)

        # main loop
        try:
            async for message in websocket:
                if message.type == WSMsgType.TEXT:
                    await self._handle_websocket_message(connection, message)

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
        # FIXME: add support for handle_user_enter
        if match and route.http_pass_through:
            http_logger.debug('http_pass_through mode')

            # load view
            view = self.view_loader.load(route.view)

            if inspect.isclass(view):
                view = view(
                    server=self,
                    view_runtime=None,
                ).handle_request

            # run view
            if asyncio.iscoroutinefunction(view):
                response = await view(http_request)

            else:
                response = await self.run_function_async(
                    view,
                    http_request,
                    excutor_name='runtime_worker',
                )

            if asyncio.iscoroutine(response):
                response = await response

            # render and return response
            if isinstance(response, dict):
                return await self.run_function_async(
                    self._render_response,
                    response,
                )

            return response

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
            connection=connection,
            window_id=None,
            url=None,
        )

        if not response_dict:
            response_dict = await self.run_function_async(
                view_runtime.start,
                excutor_name='runtime_worker',
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

    def view_is_already_running(self, *args, **kwargs):
        return self.view_runtime_controller.view_is_already_running(
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
