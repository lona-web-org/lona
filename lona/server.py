from __future__ import annotations

from typing import overload, Callable, TypeVar, List, Dict, cast, Any
from concurrent.futures import Future
from collections.abc import Awaitable
from functools import reduce
from copy import deepcopy
import contextlib
import operator
import logging
import inspect
import asyncio
import os

from aiohttp.web import (
    WebSocketResponse,
    json_response,
    FileResponse,
    Application,
    HTTPFound,
    Response,
)
from typing_extensions import Literal
from aiohttp import WSMsgType
from jinja2 import Template

from lona.responses import (
    TemplateStringResponse,
    HttpRedirectResponse,
    TemplateResponse,
    RedirectResponse,
)
from lona.compat import set_use_future_node_classes, set_client_version
from lona.view_runtime_controller import ViewRuntimeController
from lona.responses import FileResponse as LonaFileResponse
from lona.responses import AbstractResponse as LonaResponse
from lona.middleware_controller import MiddlewareController
from lona.responses import JsonResponse, HtmlResponse
from lona.static_file_loader import StaticFileLoader
from lona.templating import TemplatingEngine
from lona.imports import acquire as _acquire
from lona.worker_pool import WorkerPool
from lona.view_loader import ViewLoader
from lona.routing import Router, Route
from lona.connection import Connection
from lona.settings import Settings
from lona.request import Request
from lona.protocol import METHOD
from lona.channels import Worker
from lona.state import State
from lona.view import View

DEFAULT_SETTINGS = os.path.join(
    os.path.dirname(__file__),
    'default_settings.py',
)

server_logger = logging.getLogger('lona.server')
http_logger = logging.getLogger('lona.server.http')
websockets_logger = logging.getLogger('lona.server.websockets')

T = TypeVar('T')


class Server:
    def __init__(self, project_root: str,
                 settings_paths: List[str] | None = None,
                 settings_pre_overrides: Dict[str, Any] | None = None,
                 settings_post_overrides: Dict[str, Any] | None = None,
                 routes: List[Route] | None = None):

        self._project_root = os.path.abspath(project_root)

        self._websocket_connections: List[Connection] = []
        self._loop: asyncio.AbstractEventLoop | None = None
        self._worker_pool: WorkerPool | None = None
        self._channel_worker: List[Worker] = []

        # setup settings
        server_logger.debug('setup settings')

        self._settings_paths = [
            DEFAULT_SETTINGS,
        ]

        for path in settings_paths or []:
            self._settings_paths.append(
                os.path.normpath(
                    os.path.join(self.project_root, path),
                ),
            )

        self.settings = Settings()

        if settings_pre_overrides:
            server_logger.debug('applying settings pre overrides')

            self.settings.update(settings_pre_overrides)

        for import_string in self._settings_paths:
            server_logger.debug("loading settings from '%s'", import_string)

            self.settings.add(import_string)

        if settings_post_overrides:
            server_logger.debug('applying settings post overrides')

            self.settings.update(settings_post_overrides)

        # set feature flags
        # TODO: remove in 2.0
        set_client_version(self.settings.CLIENT_VERSION)
        set_use_future_node_classes(self.settings.USE_FUTURE_NODE_CLASSES)

        # setup aiohttp app
        server_logger.debug("starting server in '%s'", project_root)

        self._app = Application(
            client_max_size=self.settings.AIOHTTP_CLIENT_MAX_SIZE,
        )
        self._app['lona_server'] = self

        self._app.on_startup.append(self._start)
        self._app.on_shutdown.append(self._stop)

        # setup templating
        server_logger.debug('setup templating')

        self._templating_engine = TemplatingEngine(self)

        # setup state
        server_logger.debug('setup state')
        self._state = State(
            initial_data=deepcopy(self.settings.INITIAL_SERVER_STATE),
        )

        # setup routing
        server_logger.debug('setup routing')
        self._router = Router()

        if not routes:
            server_logger.debug("loading routing table from '%s'",
                                self.settings.ROUTING_TABLE)

            routes = self.acquire(self.settings.ROUTING_TABLE)

        if routes:
            self._router.add_routes(*routes)

        else:
            server_logger.warning('routing table is empty')

        # setup middleware controller
        server_logger.debug('setup middleware controller')

        self._middleware_controller = MiddlewareController(self)

        self._app.on_startup.append(
            self._middleware_controller.run_on_startup,
        )

        self._app.on_shutdown.append(
            self._middleware_controller.run_on_shutdown,
        )

        # setup aiohttp routes
        server_logger.debug('setup aiohttp routing')

        static_url = self.settings.STATIC_URL_PREFIX + '{path:.*}'

        server_logger.debug('static url set to %r', static_url)

        self._app.router.add_route(
            '*', static_url, self._handle_static_file_request)

        self._app.router.add_route(
            '*', '/{path_info:.*}', self._handle_http_request)

        # setup view loader
        server_logger.debug('setup view loader')

        self._view_loader = ViewLoader(self)

        # setup views
        server_logger.debug('setup view runtime controller')

        self._view_runtime_controller = ViewRuntimeController(self)

        # setup static files

        # the static file loader has to be started last because it does
        # node class discovery which has to happen after all views are imported
        server_logger.debug('setup static file')

        self._static_file_loader = StaticFileLoader(self)

        # finish
        server_logger.debug('setup finish')

    # properties ##############################################################
    @property
    def project_root(self):
        return self._project_root

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None:
            raise RuntimeError('loop is not set')

        return self._loop

    @property
    def worker_pool(self) -> WorkerPool:
        if self._worker_pool is None:
            raise RuntimeError('worker_pool is not set')

        return self._worker_pool

    @property
    def settings_paths(self):
        return tuple(self._settings_paths)

    @property
    def state(self):
        return self._state

    # template dirs
    @property
    def template_dirs(self):
        return tuple(self._templating_engine.template_dirs)

    @template_dirs.setter
    def template_dirs(self, new_value):
        self._templating_engine.template_dirs = new_value

    # static dirs
    @property
    def static_dirs(self):
        return tuple(self._static_file_loader.static_dirs)

    @static_dirs.setter
    def static_dirs(self, new_value):
        self._static_file_loader.static_dirs = new_value

    # start and stop ##########################################################
    async def _start(self, *args, **kwargs):
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

        self._view_runtime_controller.start()

        # setup channels
        server_logger.debug('start channels')

        message_broker_class = self.acquire(
            self.settings.CHANNEL_MESSAGE_BROKER_CLASS,
        )

        task_worker_class = self.acquire(
            self.settings.CHANNEL_TASK_WORKER_CLASS,
        )

        for _ in range(self.settings.MAX_CHANNEL_MESSAGE_BROKER_THREADS):
            self._channel_worker.append(
                message_broker_class(
                    server=self,
                    executor=self.worker_pool.get_executor('channel_worker'),
                    timeout=self.settings.CHANNEL_WORKER_TIMEOUT,
                ),
            )

        for _ in range(self.settings.MAX_CHANNEL_TASK_WORKER_THREADS):
            self._channel_worker.append(
                task_worker_class(
                    server=self,
                    executor=self.worker_pool.get_executor('channel_worker'),
                    timeout=self.settings.CHANNEL_WORKER_TIMEOUT,
                ),
            )

    async def _stop(self, *args, **kwargs):
        server_logger.debug('stop')

        for worker in self._channel_worker:
            worker.shutdown()

        await self.run_function_async(self._view_runtime_controller.stop)

        for connection in self._websocket_connections.copy():
            with contextlib.suppress(Exception):
                await connection.websocket.close()

    # connection management ###################################################
    async def _setup_connection(self, http_request, websocket=None):
        connection = Connection(self, http_request, websocket)

        handled, data, middleware = \
            await self._middleware_controller.handle_connection(
                connection,
            )

        if websocket is not None:
            self._websocket_connections.append(connection)

        return connection, (handled, data, middleware)

    def _remove_connection(self, connection):
        self._view_runtime_controller.remove_connection(connection)

        if connection in self._websocket_connections:
            self._websocket_connections.remove(connection)

    # view helper #############################################################
    def _render_response(self, lona_response):
        status = 200
        content_type = 'text/html'

        headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
        }

        # empty response
        if lona_response is None:
            return Response(
                status=status,
                content_type=content_type,
                headers=headers,
                text='',
            )

        # html responses
        if isinstance(lona_response, HtmlResponse):
            return Response(
                text=str(lona_response.html),
                status=lona_response.status or status,
                content_type=lona_response.content_type or content_type,
                headers=lona_response.headers or headers,
            )

        # template response
        if isinstance(lona_response, TemplateResponse):
            text = self.render_template(
                template_name=lona_response.name,
                template_context=lona_response.context,
            )

            return Response(
                text=text,
                status=lona_response.status or status,
                content_type=lona_response.content_type or content_type,
                headers=lona_response.headers or headers,
            )

        # template string response
        if isinstance(lona_response, TemplateStringResponse):
            text = self.render_string(
                template_string=lona_response.string,
                template_context=lona_response.context,
            )

            return Response(
                text=text,
                status=lona_response.status or status,
                content_type=lona_response.content_type or content_type,
                headers=lona_response.headers or headers,
            )

        # redirect responses
        if isinstance(lona_response, (RedirectResponse, HttpRedirectResponse)):
            raise HTTPFound(
                location=lona_response.url,
                headers=lona_response.headers or headers,
            )

        # json responses
        if isinstance(lona_response, JsonResponse):
            content_type = 'application/json'

            return json_response(
                data=lona_response.data,
                status=lona_response.status or status,
                content_type=lona_response.content_type or content_type,
                headers=lona_response.headers or headers,
            )

        # file response
        if isinstance(lona_response, LonaFileResponse):
            return FileResponse(
                path=lona_response.path,
                status=lona_response.status or status,
                headers=lona_response.headers or headers,
            )

        # fallback
        return Response(
            status=lona_response.status or status,
            content_type=lona_response.content_type or content_type,
            headers=lona_response.headers or headers,
            charset=lona_response.charset,
            body=lona_response.body,
            text=lona_response.text,
        )

    # handle http requests ####################################################
    async def _handle_static_file_request(self, request):
        def _404():
            return Response(
                status=404,
                text='404: Not found',
            )

        if not self.settings.STATIC_FILES_SERVE:
            server_logger.warning(
                'Reverse proxy seems to be misconfigured: a static file request was received but STATIC_FILES_SERVE is disabled',
            )

            return _404()

        rel_path = request.match_info['path']

        abs_path = await self.run_function_async(
            self._static_file_loader.resolve_path,
            rel_path,
            executor_name='static_worker',
        )

        if not abs_path:
            return _404()

        return FileResponse(abs_path)

    async def _handle_websocket_message(self, connection, message):
        websockets_logger.debug(
            '%s message received %s', connection, message.data)

        handled, data, middleware = \
            await self._middleware_controller.handle_websocket_message(
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
            await self.run_function_async(
                self._remove_connection,
                connection=connection,
            )

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
                    raise RuntimeError(
                        f'{middleware}.handle_connection returned non string data',
                    )

                await connection.send_str(data, wait=False)

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

        # middleware hook 'handle_http_request'
        handled, return_value, middleware = \
            await self._middleware_controller.handle_http_request(
                http_request,
            )

        if handled:
            http_logger.debug('http request got handled by %r', middleware)

            if isinstance(return_value, LonaResponse):
                return self._render_response(return_value)

            return return_value

        # resolve path
        http_logger.debug('resolving path %r', http_request.path)

        match, route, match_info = await self.run_function_async(
            self._router.resolve,
            http_request.path,
        )

        if match:
            http_logger.debug('route %s matched', route)

        else:
            http_logger.debug('no route matched')

        # http pass through ###################################################
        if match and route.http_pass_through:
            http_logger.debug('http_pass_through mode')

            # load view
            view = self._view_loader.load(route.view)

            if inspect.isclass(view):
                view = view(
                    server=self,
                    view_runtime=None,
                    request=http_request,
                ).handle_request

            # run view
            if asyncio.iscoroutinefunction(view):
                response = await view(http_request)

            else:
                response = await self.run_function_async(
                    view,
                    http_request,
                    executor_name='runtime_worker',
                )

            if asyncio.iscoroutine(response):
                response = await response

            # render and return response
            if isinstance(response, LonaResponse):
                return await self.run_function_async(
                    self._render_response,
                    response,
                )

            return response

        # websocket requests ##################################################
        if (http_request.method == 'GET' and
                (http_request.headers.get('upgrade', '').lower() ==
                    'websocket')):

            return await self._handle_websocket_request(http_request)

        # non interactive view or frontend ####################################
        # setup connection
        try:
            connection, middleware_data = await self._setup_connection(
                http_request,
            )

        except Exception:
            http_logger.exception(
                'Exception occurred while setting connection up',
            )

            return Response(status=500, body='500: Internal Error')

        handled, data, middleware = middleware_data

        # connection got closed by middleware
        if handled:
            if data is not None:
                if isinstance(data, LonaResponse):
                    return self._render_response(data)

                return data

            return Response(status=503, body='503: Service Unavailable')

        post_data = await http_request.post()

        response = await self.run_function_async(
            self._view_runtime_controller.handle_view_message,
            connection=connection,
            window_id=None,
            view_runtime_id=None,
            method=METHOD.VIEW,
            payload=[str(http_request.url), post_data],
            executor_name='runtime_worker',
        )

        return self._render_response(response)

    # public api ##############################################################
    @overload
    def run_coroutine_sync(
            self,
            coroutine: Awaitable[T],
            wait: None | Literal[True] = True,
    ) -> T:
        ...

    @overload
    def run_coroutine_sync(
            self,
            coroutine: Awaitable[T],
            wait: Literal[False],
    ) -> Future[T]:
        ...

    def run_coroutine_sync(
            self,
            coroutine: Awaitable[T],
            wait: None | bool = True,
    ) -> Future[T] | T:

        """
        Takes a coroutine, runs it thread-safe on `Server.loop` and returns
        a `concurrent.futures.Future`. If `wait` is set to `True`, the method
        blocks until the coroutine is done, and its return value is
        returned, instead of the future.

        :coroutine:  (Awaitable) coroutine
        :wait:       (bool) Wait for the coroutine to return
        """

        future = asyncio.run_coroutine_threadsafe(coroutine, loop=self.loop)

        if wait:
            return future.result()

        return future

    def run_function_async(
            self,
            function: Callable,
            *args: Any,
            executor_name: str = 'worker',
            **kwargs: Any,
    ) -> Future:

        """
        Takes a function or callable, runs it asynchronously in an thread
        executor and returns an awaitable future for the result of the given
        function.

        :function:       (callable) callable
        :args:           (list|tuple) args for the callable
        :executor_name:  (str) name of the worker pool (default is 'worker')
        :kwargs:         (dict) keyword argument for the callable
        """

        def _function():
            return function(*args, **kwargs)

        return cast(
            Future,
            self.loop.run_in_executor(
                self.worker_pool.get_executor(executor_name),
                _function,
            ),
        )

    def resolve_path(
            self,
            path: str,
    ) -> str:

        """
        Takes a path as a string and resolves it relatively to
        settings.PROJECT_ROOT.
        If the path starts with '/' the path gets returned unresolved.

        :path: (str) path
        """

        if path.startswith('/'):
            return path

        return os.path.normpath(os.path.join(self.project_root, path))

    def acquire(
            self,
            import_string: str,
            ignore_import_cache: bool = False,
    ) -> Any:

        """
        Takes an import string and returns the imported value.
        if ignore_import_cache is set, the attribute gets imported around
        Pythons import cache.

        Examples:
         - 'foo.bar.baz' (imports 'baz' from 'foo.bar')
         - 'foo/bar.py::baz' (imports 'baz' from 'foo/bar.py')

        :import_string:        (str) import string
        :ignore_import_cache:  (bool) ignore import cache as bool
        """

        if '::' in import_string:
            script, attribute_name = import_string.split('::')
            script = self.resolve_path(script)

            import_string = f'{script}::{attribute_name}'

        return _acquire(import_string, ignore_import_cache=ignore_import_cache)

    def get_running_views_count(
            self,
            user: Any,
    ) -> int:

        """
        Returns the count of running views for the given user as integer.
        """

        return cast(
            int,
            self._view_runtime_controller.get_running_views_count(user),
        )

    def view_is_already_running(
            self,
            request: Request,
    ) -> bool:

        """
        Checks if a view for the given request is already running and returns
        a boolean.

        :request:  (lona.request.Request)
        """

        view_runtime = self._view_runtime_controller.get_running_view_runtime(
            user=request.user,
            route=request.route,
            match_info=request.match_info,
        )

        return bool(view_runtime)

    def get_connection_count(
            self,
            user: Any,
    ) -> int:

        """
        Returns the count of connections for the given user as integer.

        :user: user object
        """

        count = 0

        for connection in self._websocket_connections.copy():
            if connection.user == user:
                count += 1

        return count

    def get_connected_user_count(self) -> int:
        """
        Returns the count of connected users as integer.
        """

        user: list[Any] = []

        def add_user(new_user):
            for _user in user:
                if new_user == _user:
                    return

            user.append(new_user)

        for connection in self._websocket_connections.copy():
            add_user(connection.user)

        return len(user)

    def get_template(
            self,
            template_name: str,
    ) -> Template:

        """
        Returns a Jinja2 template object associated with the given template
        name.
        """

        return cast(
            Template,
            self._templating_engine.get_template(template_name),
        )

    def render_string(
            self,
            template_string: str,
            template_context: dict | None = None,
    ) -> str:

        """
        Takes a Jinja2 template as a string and returns the rendering result
        as string. If no template context is given, an empty one is used.

        All values in settings.TEMPLATE_EXTRA_CONTEXT get added to the
        template context before rendering.

        :template_string:  (str) Jinja2 template as string
        :template_context: (dict|none) template context as dictionary
        """

        return cast(
            str,
            self._templating_engine.render_string(
                template_string=template_string,
                template_context=template_context,
            ),
        )

    def render_template(
            self,
            template_name: str,
            template_context: dict | None = None,
    ) -> str:

        """
        Takes the name of a Jinja2 template as a string, searches for a
        matching template in settings.TEMPLATE_DIRS and returns the rendering
        result as string. If no template context is given, an empty
        one is used.

        All values in settings.TEMPLATE_EXTRA_CONTEXT get added to the
        template context before rendering.

        :template_name:    (str) Jinja2 template as string
        :template_context: (dict|none) template context as dictionary
        """

        return cast(
            str,
            self._templating_engine.render_template(
                template_name=template_name,
                template_context=template_context,
            ),
        )

    def get_view_class(
            self,
            route_name: str | None = None,
            route: Route | None = None,
            import_string: str | None = None,
            url: str | None = None,
    ) -> type[View] | None:

        """
        Returns the lona.view.View subclass associated with the given
        route_name, route, import string or url.

        Only one argument can be set at a time.
        """

        args = [bool(route_name), bool(route), bool(import_string), bool(url)]

        if reduce(operator.xor, args, True):
            raise ValueError('too many or too few arguments given')

        if route_name:
            route = self._router.get_route(name=route_name)

            if not route:
                return None

        if route:
            view = route.view

        if import_string:
            view = import_string

        if url:
            success, route, match_info = self._router.resolve(url)

            if not success:
                return None

            route = cast(Route, route)
            view = route.view

        return self._view_loader.load(view)

    def get_views(
            self,
            route_name: str | None = None,
            route: Route | None = None,
            import_string: str | None = None,
            url: str | None = None,
            user: Any = None,
    ) -> list[View]:

        """
        Returns a list of all running Lona views associated with the given
        route_name, route, import string or url.

        Only one argument to find the view can be set at a time. User can
        always be set.

        :route:          (lona.Route|none) Lona route associated with the view
        :import_string:  (str|none) import string of the view
        :url:            (str|none) URL to the view
        :user:           (any) User that runs th view (optional)
        """

        view_class = self.get_view_class(
            route_name=route_name,
            route=route,
            import_string=import_string,
            url=url,
        )

        if not view_class:
            return []

        views = self._view_runtime_controller.get_views(view_class=view_class)

        if user:
            for view in views.copy():
                if view.request.user is not user:
                    views.remove(view)

        return views

    def reverse(
            self,
            route_name: str,
            *args: Any,
            **kwargs: dict[str, Any],
    ) -> str:

        """
        Returns a routing reverse match as string.

        :route_name:  (str) route name as string
        :args:        route arguments
        :kwargs:      route keyword argument
        """

        return cast(
            str,
            self._router.reverse(
                route_name=route_name,
                *args,
                **kwargs,
            ),
        )

    def fire_view_event(
            self,
            name: str,
            data: dict | None = None,
            view_classes: type[View] | list[type[View]] | None = None,
    ) -> None:

        """
        Sends a view event to all objects of the given View class.
        If view_classes is not set, the event becomes a broadcast event and
        gets send to all view classes.

        :name: has to be a str, data is optional but has to be a dict if set.
        :view_classes: can be a single view class or a list of view classes.

        Examples:

            # broadcast event
            server.fire_view_event('foo', {'foo': 'bar'})

            # event for all view objects behind the URL '/foo'
            server.fire_view_event(
                'foo',
                {'foo': 'bar'},
                view_classes=server.get_view_class(url='/foo'),
            )
        """

        self._view_runtime_controller.fire_view_event(
            name=name,
            data=data,
            view_classes=view_classes,
        )
