from typing import (
    TYPE_CHECKING,
    Awaitable,
    overload,
    Optional,
    Iterator,
    Callable,
    TypeVar,
    Union,
    Tuple,
    Type,
    List,
    Dict,
    cast,
)
from concurrent.futures import CancelledError
import threading
import asyncio

from typing_extensions import Literal
from jinja2.nodes import Template

from lona.view_runtime import VIEW_RUNTIME_STATE, ViewRuntime
from lona.exceptions import ServerStop, UserAbort
from lona.html.abstract_node import AbstractNode
from lona.events.input_event import InputEvent
from lona.shell.shell import embed_shell
from lona.connection import Connection
from lona.errors import ClientError
from lona.request import Request

# avoid import cycles
if TYPE_CHECKING:
    from lona.server import LonaServer


_T = TypeVar('_T')
_V = TypeVar('_V', bound='LonaView')
_HTML = Union[None, AbstractNode, str]


class LonaView:
    _objects: Dict[str, List['LonaView']] = {}

    def __init__(
            self,
            server: 'LonaServer',
            view_runtime: ViewRuntime,
            request: Request,
    ) -> None:
        self._server: 'LonaServer' = server
        self._view_runtime: ViewRuntime = view_runtime
        self._request: Request = request

    # objects #################################################################
    @overload
    @classmethod
    def _get_objects_key(
            cls,
            view_class: Type['LonaView'],
            is_class: Literal[True],
    ) -> str:
        ...

    @overload
    @classmethod
    def _get_objects_key(
            cls,
            view_class: 'LonaView',
            is_class: Literal[False],
    ) -> str:
        ...

    @classmethod
    def _get_objects_key(cls, view_class, is_class):
        if not is_class:
            view_class = view_class.__class__

        return f'{view_class.__module__}.{view_class.__name__}'

    @classmethod
    def _add_view_to_objects(cls, view_object: 'LonaView') -> None:
        objects_key = cls._get_objects_key(view_object, is_class=False)

        if objects_key not in cls._objects:
            cls._objects[objects_key] = []

        cls._objects[objects_key].append(view_object)

    @classmethod
    def _remove_view_from_objects(cls, view_object: 'LonaView') -> None:
        objects_key = cls._get_objects_key(view_object, is_class=False)

        if(objects_key in cls._objects and
           view_object in cls._objects[objects_key]):

            cls._objects[objects_key].remove(view_object)

    @classmethod
    def iter_objects(cls: Type[_V]) -> Iterator[_V]:
        objects_key = cls._get_objects_key(cls, is_class=True)
        view_objects = cls._objects.get(objects_key, []).copy()
        yield from view_objects  # type: ignore

    # properties ##############################################################
    @property
    def server(self) -> 'LonaServer':
        return self._server

    @property
    def request(self) -> Request:
        return self._request

    # checks ##################################################################
    def _assert_not_main_thread(self) -> None:
        if threading.current_thread() is threading.main_thread():
            raise RuntimeError(
                'this function is not supposed to run in the main thread')

    def _assert_view_is_interactive(self) -> None:
        if not self._request.route.interactive:
            raise RuntimeError(
                'operation is not supported in non-interactive requests')

    def _assert_view_is_running(self) -> None:
        if self._view_runtime.stop_reason:
            raise self._view_runtime.stop_reason

    # asyncio #################################################################
    def _await_sync(self, awaitable: Awaitable[_T]) -> _T:
        async def await_awaitable() -> _T:
            finished, pending = await asyncio.wait(
                [
                    cast(Awaitable, self._view_runtime.stopped),
                    awaitable,
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for finished_future in finished:
                if finished_future is not self._view_runtime.stopped:
                    return finished_future.result()

            if self._view_runtime.stopped in finished:
                for pending_future in pending:
                    if not pending_future.done():
                        pending_future.cancel()

            raise self._view_runtime.stop_reason

        return asyncio.run_coroutine_threadsafe(
            await_awaitable(),
            loop=self._server.loop,
        ).result()

    def await_sync(self, awaitable: Awaitable[_T]) -> _T:
        self._view_runtime.state = VIEW_RUNTIME_STATE.WAITING_FOR_IOLOOP

        try:
            return self._await_sync(awaitable)

        finally:
            self._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING

    # html ####################################################################
    def show(
            self,
            html: _HTML = None,
            template: Union[None, str, Template] = None,
            template_string: Union[None, str, Template] = None,
            title: Optional[str] = None,
            template_context: Optional[dict] = None,
    ) -> None:
        self._assert_not_main_thread()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        # templating
        if template or template_string:
            template_context = template_context or {}

            if 'template_context' in template_context:
                template_context = template_context['template_context']

            # string based templates
            if template_string:
                html = self._server.templating_engine.render_string(
                    template_string=template_string,
                    template_context=template_context,
                )

            # file based templates
            else:
                html = self._server.templating_engine.render_template(
                    template_name=template,
                    template_context=template_context,
                )

        with self._view_runtime.document.lock:
            html = html or self._view_runtime.document.html
            data = self._view_runtime.document.apply(html)

            if data:
                self._view_runtime.send_data(data=data, title=title)

    def set_title(self, title: str) -> None:
        self._assert_not_main_thread()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        with self._view_runtime.document.lock:
            self._view_runtime.send_data(title=title)

    # messaging ###############################################################
    def send_str(
            self,
            string: str,
            broadcast: bool = False,
            filter_connections: Callable[[Connection], bool] = lambda c: True,
            wait: bool = True,
    ) -> None:
        self._assert_not_main_thread()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        # broadcast
        if broadcast:
            for connection in self.server.websocket_connections.copy():
                if not filter_connections(connection):
                    continue

                connection.send_str(string, wait=wait)

        # view local
        else:
            runtime = self._view_runtime

            with runtime.document.lock:
                for connection in list(runtime.connections.keys()):
                    if not connection.interactive:
                        continue

                    connection.send_str(string, wait=wait)

    # input events ############################################################
    def _await_specific_input_event(
            self,
            *nodes: Union[AbstractNode, List[AbstractNode]],
            event_type: str = '',
            html: _HTML = None,
    ) -> InputEvent:
        self._view_runtime.state = VIEW_RUNTIME_STATE.WAITING_FOR_INPUT

        try:
            self._assert_not_main_thread()
            self._assert_view_is_interactive()
            self._assert_view_is_running()

            if len(nodes) == 1 and isinstance(nodes[0], list):
                nodes = tuple(nodes[0])

            nodes = cast(Tuple[AbstractNode], nodes)

            if html is not None:
                self.show(html=html)

            return self._view_runtime.await_input_event(
                nodes=nodes,
                event_type=event_type,
            )

        finally:
            self._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING

    @overload
    def await_input_event(self, *nodes: AbstractNode, html: _HTML = None) -> InputEvent:  # NOQA: LN001
        ...

    @overload
    def await_input_event(self, __nodes: List[AbstractNode], html: _HTML = None) -> InputEvent:  # NOQA: LN001
        ...

    def await_input_event(self, *nodes, html=None):
        return self._await_specific_input_event(
            *nodes,
            event_type='event',
            html=html,
        )

    @overload
    def await_click(self, *nodes: AbstractNode, html: _HTML = None) -> InputEvent:  # NOQA: LN001
        ...

    @overload
    def await_click(self, __nodes: List[AbstractNode], html: _HTML = None) -> InputEvent:  # NOQA: LN001
        ...

    def await_click(self, *nodes, html=None):
        return self._await_specific_input_event(
            *nodes,
            event_type='click',
            html=html,
        )

    @overload
    def await_change(self, *nodes: AbstractNode, html: _HTML = None) -> InputEvent:  # NOQA: LN001
        ...

    @overload
    def await_change(self, __nodes: List[AbstractNode], html: _HTML = None) -> InputEvent:  # NOQA: LN001
        ...

    def await_change(self, *nodes, html=None):
        return self._await_specific_input_event(
            *nodes,
            event_type='change',
            html=html,
        )

    # runtime #################################################################
    @overload
    def sleep(self, delay: float) -> None:
        ...

    @overload
    def sleep(self, delay: float, result: _T) -> _T:
        ...

    def sleep(self, delay: float, result: Optional[_T] = None) -> Optional[_T]:
        self._view_runtime.state = VIEW_RUNTIME_STATE.SLEEPING

        try:
            return self._await_sync(asyncio.sleep(delay, result))

        finally:
            self._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING

    def daemonize(self) -> None:
        self._assert_view_is_interactive()

        self._view_runtime.is_daemon = True

    def ping(self) -> Literal['pong']:
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        return 'pong'

    # helper ##################################################################
    def embed_shell(self, _locals: Optional[dict] = None) -> None:
        if _locals is None:
            _locals = {}
        _locals['self'] = self

        embed_shell(server=self.server, locals=_locals)

    # hooks ###################################################################
    def handle_request(self, request: Request) -> Union[None, str, AbstractNode, dict]:  # NOQA: LN001
        return ''

    def handle_input_event_root(self, input_event: InputEvent) -> Optional[InputEvent]:  # NOQA: LN001
        return input_event

    def handle_input_event(self, input_event: InputEvent) -> Optional[InputEvent]:  # NOQA: LN001
        return input_event

    def on_shutdown(
            self,
            reason: Union[
                None,
                UserAbort,
                ServerStop,
                CancelledError,
                ClientError,
                Exception,
            ],
    ) -> None:
        pass
