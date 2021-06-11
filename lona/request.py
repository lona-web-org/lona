import threading
import asyncio

from lona.symbols import VIEW_RUNTIME_STATE
from lona.types import Symbol


class Client:
    def __init__(self, request):
        self.request = request

    def _assert_not_main_thread(self):
        if threading.current_thread() is threading.main_thread():
            raise RuntimeError(
                'this function is not supposed to run in the main thread')

    def _assert_view_is_interactive(self):
        if not self.request._view_runtime.route.interactive:
            raise RuntimeError(
                'operation is not supported in non-interactive requests')

    def _assert_view_is_running(self):
        if self.request._view_runtime.stop_reason:
            raise self.request._view_runtime.stop_reason

    def _await_specific_input_event(self, *nodes, event_type='', html=None):
        self.request._view_runtime.state = VIEW_RUNTIME_STATE.WAITING_FOR_INPUT

        try:
            self._assert_not_main_thread()
            self._assert_view_is_interactive()
            self._assert_view_is_running()

            if nodes:
                nodes = list(nodes)

            if len(nodes) == 1 and isinstance(nodes[0], list):
                nodes = nodes[0]

            if html is not None:
                self.show(html=html)

            return self.request._view_runtime.await_input_event(
                nodes=nodes,
                event_type=event_type,
            )

        finally:
            self.request._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING

    def ping(self):
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        return 'pong'

    def show(self, html=None, template=None, template_string=None, title=None,
             template_context=None):

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
                html = self.request.server.templating_engine.render_string(
                    template_string=template_string,
                    template_context=template_context,
                )

            # file based templates
            else:
                html = self.request.server.templating_engine.render_template(
                    template_name=template,
                    template_context=template_context,
                )

        with self.request._view_runtime.document.lock:
            html = html or self.request._view_runtime.document.html
            data = self.request._view_runtime.document.apply(html)

            if data:
                self.request._view_runtime.send_data(data=data, title=title)

    def set_title(self, title):
        self._assert_not_main_thread()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        with self.request._view_runtime.document.lock:
            self.request._view_runtime.send_data(title=title)

    def send_str(self, string, broadcast=False):
        self._assert_not_main_thread()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        if not broadcast:
            self.request.connection.send_str(string, sync=True)

            return

        for connection in self.request.server.websocket_connections:
            connection.send_str(string, sync=True)

    def await_input_event(self, *nodes, html=None):
        return self. _await_specific_input_event(
            *nodes,
            event_type='event',
            html=html,
        )

    def await_click(self, *nodes, html=None):
        return self. _await_specific_input_event(
            *nodes,
            event_type='click',
            html=html,
        )

    def await_change(self, *nodes, html=None):
        return self. _await_specific_input_event(
            *nodes,
            event_type='change',
            html=html,
        )

    def await_submit(self, *nodes, html=None):
        return self. _await_specific_input_event(
            *nodes,
            event_type='submit',
            html=html,
        )


class View:
    def __init__(self, request):
        self.request = request

    def daemonize(self):
        self.request.client._assert_view_is_interactive()

        self.request._view_runtime.is_daemon = True

    def _await_sync(self, awaitable):
        async def await_awaitable():
            finished, pending = await asyncio.wait(
                [
                    self.request._view_runtime.stopped,
                    awaitable,
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for finished_future in finished:
                if finished_future is not self.request._view_runtime.stopped:
                    return finished_future.result()

            if self.request._view_runtime.stopped in finished:
                for pending_future in pending:
                    if not pending_future.done():
                        pending_future.cancel()

                raise self.request._view_runtime.stop_reason

        return asyncio.run_coroutine_threadsafe(
            await_awaitable(),
            loop=self.request.server.loop,
        ).result()

    def await_sync(self, *args, **kwargs):
        self.request._view_runtime.state = \
            VIEW_RUNTIME_STATE.WAITING_FOR_IOLOOP

        try:
            return self._await_sync(*args, **kwargs)

        finally:
            self.request._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING

    def sleep(self, *args, **kwargs):
        self.request._view_runtime.state = VIEW_RUNTIME_STATE.SLEEPING

        try:
            return self._await_sync(asyncio.sleep(*args, **kwargs))

        finally:
            self.request._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING


class Request:
    def __init__(self, view_runtime, connection):
        self._view_runtime = view_runtime
        self.connection = connection

        self.url = self._view_runtime.url

        if self.url:
            self.GET = dict(self._view_runtime.url.query)
            self.POST = self._view_runtime.post_data or {}

        else:
            self.GET = {}
            self.POST = {}

        self.method = Symbol('POST' if self.POST else 'GET')

        self.server = self._view_runtime.server
        self.route = self._view_runtime.route
        self.match_info = self._view_runtime.match_info

        self.client = Client(self)
        self.view = View(self)

    @property
    def user(self):
        return getattr(self.connection, 'user', None)

    @property
    def frontend(self):
        return self._view_runtime.frontend
