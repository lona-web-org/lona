import threading
import asyncio

from lona.view_runtime import VIEW_RUNTIME_STATE
from lona.shell.shell import embed_shell


class LonaView:
    _objects = {}

    def __init__(self, server, view_runtime, request):
        self._server = server
        self._view_runtime = view_runtime
        self._request = request

    # objects #################################################################
    @classmethod
    def _get_objects_key(cls, view_class, is_class=True):
        if not is_class:
            view_class = view_class.__class__

        return '{}.{}'.format(
            view_class.__module__,
            view_class.__name__,
        )

    @classmethod
    def _add_view_to_objects(cls, view_object):
        objects_key = cls._get_objects_key(view_object, is_class=False)

        if objects_key not in cls._objects:
            cls._objects[objects_key] = []

        cls._objects[objects_key].append(view_object)

    @classmethod
    def _remove_view_from_objects(cls, view_object):
        objects_key = cls._get_objects_key(view_object, is_class=False)

        if(objects_key in cls._objects and
           view_object in cls._objects[objects_key]):

            cls._objects[objects_key].remove(view_object)

    @classmethod
    def iter_objects(cls):
        objects_key = cls._get_objects_key(cls, is_class=True)
        view_objects = cls._objects.get(objects_key, []).copy()

        for view_object in view_objects:
            yield view_object

    # properties ##############################################################
    @property
    def server(self):
        return self._server

    @property
    def request(self):
        return self._request

    # checks ##################################################################
    def _assert_not_main_thread(self):
        if threading.current_thread() is threading.main_thread():
            raise RuntimeError(
                'this function is not supposed to run in the main thread')

    def _assert_view_is_interactive(self):
        if not self._request.route.interactive:
            raise RuntimeError(
                'operation is not supported in non-interactive requests')

    def _assert_view_is_running(self):
        if self._view_runtime.stop_reason:
            raise self._view_runtime.stop_reason

    # asyncio #################################################################
    def _await_sync(self, awaitable):
        async def await_awaitable():
            finished, pending = await asyncio.wait(
                [
                    self._view_runtime.stopped,
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

    def await_sync(self, *args, **kwargs):
        self._view_runtime.state = VIEW_RUNTIME_STATE.WAITING_FOR_IOLOOP

        try:
            return self._await_sync(*args, **kwargs)

        finally:
            self._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING

    # html ####################################################################
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

    def set_title(self, title):
        self._assert_not_main_thread()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        with self._view_runtime.document.lock:
            self._view_runtime.send_data(title=title)

    # messaging ###############################################################
    def send_str(self, string, broadcast=False,
                 filter_connections=lambda connection: True, wait=True):

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
    def _await_specific_input_event(self, *nodes, event_type='', html=None):
        self._view_runtime.state = VIEW_RUNTIME_STATE.WAITING_FOR_INPUT

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

            return self._view_runtime.await_input_event(
                nodes=nodes,
                event_type=event_type,
            )

        finally:
            self._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING

    def await_input_event(self, *nodes, html=None):
        return self._await_specific_input_event(
            *nodes,
            event_type='event',
            html=html,
        )

    def await_click(self, *nodes, html=None):
        return self._await_specific_input_event(
            *nodes,
            event_type='click',
            html=html,
        )

    def await_change(self, *nodes, html=None):
        return self._await_specific_input_event(
            *nodes,
            event_type='change',
            html=html,
        )

    # runtime #################################################################
    def sleep(self, *args, **kwargs):
        self._view_runtime.state = VIEW_RUNTIME_STATE.SLEEPING

        try:
            return self._await_sync(asyncio.sleep(*args, **kwargs))

        finally:
            self._view_runtime.state = VIEW_RUNTIME_STATE.RUNNING

    def daemonize(self):
        self._assert_view_is_interactive()

        self._view_runtime.is_daemon = True

    def ping(self):
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        return 'pong'

    # helper ##################################################################
    def embed_shell(self, _locals={}):
        _locals['self'] = self

        return embed_shell(server=self.server, locals=_locals)

    # hooks ###################################################################
    def handle_request(self, request):
        return ''

    def handle_input_event_root(self, input_event):
        return input_event

    def handle_input_event(self, input_event):
        return input_event

    def on_shutdown(self, reason):
        pass
