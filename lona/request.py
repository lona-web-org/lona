import asyncio

from lona.context import current_thread_is_main_thread
from lona.types import Symbol


class Client:
    def __init__(self, request):
        self.request = request

    def _assert_not_main_thread(self):
        if current_thread_is_main_thread():
            raise RuntimeError(
                'this function is not supposed to run in the main thread')

    def _assert_single_user_request(self):
        if self.request._view_runtime.view_spec.multi_user:
            raise RuntimeError(
                'operation is not supported in multi user requests')

    def _assert_view_is_interactive(self):
        if not self.request._view_runtime.route.interactive:
            raise RuntimeError(
                'operation is not supported in non-interactive requests')

    def _assert_view_is_running(self):
        if self.request._view_runtime.stop_reason:
            raise self.request._view_runtime.stop_reason

    def _await_specific_input_event(self, *nodes, event_type='', **kwargs):
        self._assert_not_main_thread()
        self._assert_single_user_request()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        if nodes:
            nodes = list(nodes)

        if len(nodes) == 1 and isinstance(nodes[0], list):
            nodes = nodes[0]

        if kwargs:
            self.show(**kwargs)

        return self.request._view_runtime.await_input_event(
            nodes=nodes,
            event_type=event_type,
        )

    def ping(self):
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        return 'pong'

    def show(self, html=None, template=None, template_string=None, title=None,
             **kwargs):

        self._assert_not_main_thread()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        # templating
        if template or template_string:
            template_context = kwargs

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

        with self.request._view_runtime.document.lock():
            html = html or self.request._view_runtime.document.html
            data = self.request._view_runtime.document.apply(html)

            if data:
                self.request._view_runtime.send_data(data=data, title=title)

    def set_title(self, title):
        self._assert_not_main_thread()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        with self.request._view_runtime.document.lock():
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

    def await_input_event(self, **kwargs):
        return self. _await_specific_input_event(
            event_type='event',
            **kwargs,
        )

    def await_click(self, *clickable_nodes, **kwargs):
        return self. _await_specific_input_event(
            *clickable_nodes,
            event_type='click',
            **kwargs,
        )

    def await_change(self, *changeable_nodes, **kwargs):
        return self. _await_specific_input_event(
            *changeable_nodes,
            event_type='change',
            **kwargs,
        )

    def await_submit(self, *form_nodes, **kwargs):
        return self. _await_specific_input_event(
            *form_nodes,
            event_type='submit',
            **kwargs,
        )


class View:
    def __init__(self, request):
        self.request = request

    def _assert_single_user_request(self):
        if self.request._view_runtime.view_spec.multi_user:
            raise RuntimeError(
                'operation is not supported in multi user requests')

    def daemonize(self):
        self.request.client._assert_view_is_interactive()
        self.request.client._assert_single_user_request()

        self.request._view_runtime.is_daemon = True

    def await_sync(self, awaitable):
        async def _await(future):
            return await future

        if asyncio.isfuture(awaitable):
            awaitable = _await(awaitable)

        concurrent_future = asyncio.run_coroutine_threadsafe(
            asyncio.wait(
                [
                    self.request._view_runtime.stopped,
                    awaitable,
                ],
                return_when=asyncio.FIRST_COMPLETED,
            ),
            loop=self.request.server.loop,
        )

        finished, pending = concurrent_future.result()

        finished = finished.pop()
        pending = pending.pop()

        if finished is self.request._view_runtime.stopped:
            pending.cancel()

            raise self.request._view_runtime.stop_reason

        return finished.result()

    def sleep(self, *args, **kwargs):
        return self.await_sync(asyncio.sleep(*args, **kwargs))


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
        if self._view_runtime.view_spec.multi_user:
            user = []

            for connection in self._view_runtime.connections.keys():
                user.append(connection.user)

            return user

        return getattr(self.connection, 'user', None)

    @property
    def frontend(self):
        return self._view_runtime.frontend
