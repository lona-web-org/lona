class Client:
    def __init__(self, request):
        self.request = request

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
            raise self.request._view_runtime.stop_reason()

    def _await_specific_input_event(self, *nodes, html=None, event_type=''):
        self._assert_single_user_request()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        if nodes:
            nodes = list(nodes)

        if len(nodes) == 1 and isinstance(nodes[0], list):
            nodes = nodes[0]

        return self.request._view_runtime.await_input_event(
            html=html,
            event_type=event_type,
            nodes=nodes,
        )

    def ping(self):
        self._assert_view_is_running()

        return 'pong'

    def show(self, html=None, title=None):
        self._assert_view_is_running()

        with self.request._view_runtime.document.lock():
            html = html or self.request._view_runtime.document.html
            html_data = self.request._view_runtime.document.apply(html)

            if html_data:
                self.request._view_runtime.send_data(
                    html_data=html_data,
                    title=title,
                )

    def set_title(self, title):
        self._assert_view_is_running()

        with self.request._view_runtime.document.lock():
            self.request._view_runtime.send_data(title=title)

    def await_input_event(self, html=None):
        self._assert_single_user_request()
        self._assert_view_is_interactive()
        self._assert_view_is_running()

        return self.request._view_runtime.await_input_event(html=html)

    def await_click(self, *clickable_nodes, html=None):
        return self. _await_specific_input_event(
            *clickable_nodes,
            html=html,
            event_type='click',
        )

    def await_change(self, *changeable_nodes, html=None):
        return self. _await_specific_input_event(
            *changeable_nodes,
            html=html,
            event_type='change',
        )

    def await_submit(self, *form_nodes, html=None):
        return self. _await_specific_input_event(
            *form_nodes,
            html=html,
            event_type='submit',
        )


class View:
    def __init__(self, request):
        self.request = request

    def _assert_single_user_request(self):
        if self.request._view_runtime.view_spec.multi_user:
            raise RuntimeError(
                'operation is not supported in multi user requests')

    def daemonize(self):
        self._assert_single_user_request()

        self.request._view_runtime.is_daemon = True


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

        self.method = 'POST' if self.POST else 'GET'

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
