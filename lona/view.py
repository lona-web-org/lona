from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Union, List, cast
from collections.abc import Awaitable, Callable
import threading
import asyncio

from typing_extensions import Literal

from lona.view_runtime import VIEW_RUNTIME_STATE, ViewRuntime
from lona.html.abstract_node import AbstractNode
from lona.events.input_event import InputEvent
from lona.static_files import StaticFile
from lona.exceptions import StopReason
from lona.connection import Connection
from lona.channels import Channel
from lona.request import Request

# avoid import cycles
if TYPE_CHECKING:  # pragma: no cover
    from lona.events.view_event import ViewEvent
    from lona.server import Server

T = TypeVar('T')
V = TypeVar('V', bound='View')
H = Union[None, AbstractNode, str]


class View:
    STATIC_FILES: list[StaticFile] = []

    def __init__(
            self,
            server: Server,
            view_runtime: ViewRuntime,
            request: Request,
    ) -> None:
        self._server: Server = server
        self._view_runtime: ViewRuntime = view_runtime
        self._request: Request = request
        self._channels: List[Channel] = []

    def _cleanup(self):
        self.unsubscribe_from_all_channels()

    # properties ##############################################################
    @property
    def server(self) -> Server:
        return self._server

    @property
    def request(self) -> Request:
        return self._request

    # is_daemon
    @property
    def is_daemon(self) -> bool:
        return bool(self._view_runtime.is_daemon)

    @is_daemon.setter
    def is_daemon(self, value: bool) -> None:
        self._assert_view_is_interactive()

        self._view_runtime.is_daemon = bool(value)

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
    def _await_sync(self, awaitable: Awaitable[T]) -> T:
        if asyncio.iscoroutine(awaitable):
            awaitable = self.server.loop.create_task(awaitable)

        async def await_awaitable() -> T:
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

            raise cast(StopReason, self._view_runtime.stop_reason)

        return asyncio.run_coroutine_threadsafe(
            await_awaitable(),
            loop=self._server.loop,
        ).result()

    def await_sync(self, awaitable: Awaitable[T]) -> T:
        self._view_runtime.state = VIEW_RUNTIME_STATE.WAITING_FOR_IOLOOP

        try:
            return self._await_sync(awaitable)

        finally:
            self._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING

    # html ####################################################################
    def show(
            self,
            html: H = None,
            template: None | str = None,
            template_string: None | str = None,
            title: None | str = None,
            template_context: None | dict = None,
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
                html = self._server.render_string(
                    template_string=template_string,
                    template_context=template_context,
                )

            # file based templates
            else:
                html = self._server.render_template(
                    template_name=cast(str, template),
                    template_context=template_context,
                )

        with self._view_runtime.document.lock:
            html = html or self._view_runtime.document.html

            title, data_type, data = self._view_runtime.document.apply(
                title=title,
                html=html,
            )

            if data_type and data:
                self._view_runtime.send_data(
                    title=title,
                    data=[data_type, data],
                )

    def set_title(self, title: str) -> None:
        self._assert_not_main_thread()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        title, _, _ = self._view_runtime.document.apply(title=title)

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
            for connection in self.server._websocket_connections.copy():
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
            *nodes: AbstractNode | list[AbstractNode],
            event_type: str = '',
            html: H = None,
    ) -> InputEvent:
        self._view_runtime.state = VIEW_RUNTIME_STATE.WAITING_FOR_INPUT

        try:
            self._assert_not_main_thread()
            self._assert_view_is_interactive()
            self._assert_view_is_running()

            if len(nodes) == 1 and isinstance(nodes[0], list):
                nodes = tuple(nodes[0])

            nodes = cast('tuple[AbstractNode]', nodes)

            if html is not None:
                self.show(html=html)

            return self._view_runtime.await_input_event(
                nodes=nodes,
                event_type=event_type,
            )

        finally:
            self._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING

    def await_input_event(
            self,
            *nodes: list[AbstractNode],
            html: H = None,
    ) -> InputEvent:

        return self._await_specific_input_event(
            *nodes,
            event_type='event',
            html=html,
        )

    def await_click(
            self,
            *nodes: list[AbstractNode],
            html: H = None,
    ) -> InputEvent:

        return self._await_specific_input_event(
            *nodes,
            event_type='click',
            html=html,
        )

    def await_change(
            self,
            *nodes: list[AbstractNode],
            html: H = None,
    ) -> InputEvent:

        return self._await_specific_input_event(
            *nodes,
            event_type='change',
            html=html,
        )

    def await_focus(
            self,
            *nodes: list[AbstractNode],
            html: H = None,
    ) -> InputEvent:

        return self._await_specific_input_event(
            *nodes,
            event_type='focus',
            html=html,
        )

    def await_blur(
            self,
            *nodes: list[AbstractNode],
            html: H = None,
    ) -> InputEvent:

        return self._await_specific_input_event(
            *nodes,
            event_type='blur',
            html=html,
        )

    # view events #############################################################
    def fire_view_event(self, name: str, data: dict | None = None) -> None:
        self.server._view_runtime_controller.fire_view_event(
            name=name,
            data=data,
            view_classes=[self.__class__],
        )

    # channels ################################################################
    def subscribe(
            self,
            topic: str,
            handler: Callable,
            implicit_show: bool = True,
    ) -> Channel:

        def _handler(*args, **kwargs):
            try:
                handler(*args, **kwargs)

                if implicit_show:
                    self.show()

            except Exception as exception:
                self._view_runtime.issue_500_error(exception=exception)
                channel.unsubscribe()

                if not isinstance(exception, StopReason):
                    raise

        channel = Channel(topic=topic, handler=_handler)

        self._channels.append(channel)

        return channel

    def unsubscribe_from_all_channels(self) -> None:
        for channel in self._channels:
            channel.unsubscribe()

    # runtime #################################################################
    def sleep(self, delay: float, result: T | None = None) -> T | None:
        self._view_runtime.state = VIEW_RUNTIME_STATE.SLEEPING

        try:
            return self._await_sync(asyncio.sleep(delay, result))

        finally:
            self._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING

    def daemonize(self) -> None:
        # TODO: remove in 2.0

        self.is_daemon = True

    def ping(self) -> Literal['pong']:
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        return 'pong'

    # hooks ###################################################################
    def handle_request(self, request: Request) -> None | str | AbstractNode | dict:  # NOQA: LN001
        return ''

    def handle_input_event_root(
            self,
            input_event: InputEvent,
    ) -> InputEvent | dict | None:

        return input_event

    def handle_input_event(
            self,
            input_event: InputEvent,
    ) -> InputEvent | dict | None:

        return input_event

    def on_view_event(self, view_event: 'ViewEvent') -> dict | None:
        pass

    def on_stop(self, reason: Exception | None) -> None:
        pass

    def on_cleanup(self) -> None:
        pass


LonaView = View  # TODO: remove in 2.0
