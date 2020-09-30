class Client:
    # TODO: user input: add check if view is interactive

    def __init__(self, request):
        self.request = request

    def _assert_single_user_request(self):
        if self.request._multi_user:
            raise RuntimeError(
                'operation is not supported in multi user requests')

    def _assert_view_is_running(self):
        if self.request._view.shutdown_error_class:
            raise self.request._view.shutdown_error_class()

    def show(self, html=None, patch_input_events=True, flush=False):
        self._assert_view_is_running()

        if self.request._multi_user:
            patch_input_events = False

        self.request._view.send_data(
            html=html,
            patch_input_events=patch_input_events,
        )

    def set_title(self, title):
        self._assert_view_is_running()

        self.request._view.send_data(title=title)

    def await_user_input(self, html=None):
        self._assert_single_user_request()
        self._assert_view_is_running()

        return self.request._view.await_user_input(html=html)

    def await_click(self, *clickable_nodes, html=None):
        self._assert_single_user_request()
        self._assert_view_is_running()

        nodes = clickable_nodes

        if nodes:
            nodes = list(nodes)

        if len(nodes) == 1 and isinstance(nodes[0], list):
            nodes = nodes[0]

        return self.request._view.await_user_input(
            html=html,
            event_type='click',
            nodes=nodes,
        )


class View:
    def __init__(self, request):
        self.request = request

    def _assert_single_user_request(self):
        if self.request._multi_user:
            raise RuntimeError(
                'operation is not supported in multi user requests')

    def daemonize(self):
        self._assert_single_user_request()

        self.request._view.is_daemon = True


class Request:
    def __init__(self, view, connection, post_data, multi_user=False):
        self._view = view
        self._multi_user = multi_user
        self.connection = connection

        self.url = self._view.url

        if self.url:
            self.GET = dict(self._view.url.query)
            self.POST = post_data or {}

        else:
            self.GET = {}
            self.POST = {}

        self.method = 'POST' if self.POST else 'GET'

        self.server = self._view.server
        self.route = self._view.route
        self.match_info = self._view.match_info

        self.client = Client(self)
        self.view = View(self)

    @property
    def user(self):
        # TODO: return user list if multi_user flag is set

        return getattr(self.connection, 'user', None)
