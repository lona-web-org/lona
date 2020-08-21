class Client:
    def __init__(self, view):
        self._view = view

    def show(self, html=None, input_events=True, flush=False):
        if self._view.shutdown_error_class:
            raise self._view.shutdown_error_class()

        self._view.show_html(html, input_events=input_events)

    def await_user_input(self, html=None):
        return self._view.await_user_input(html=html)

    def await_click(self, *clickable_nodes, html=None):
        nodes = clickable_nodes

        if nodes:
            nodes = list(nodes)

        if len(nodes) == 1 and isinstance(nodes[0], list):
            nodes = nodes[0]

        return self._view.await_user_input(
            html=html,
            event_type='click',
            nodes=nodes,
        )


class Request:
    def __init__(self, view, post_data):
        self._view = view

        self.url = self._view.url
        self.GET = dict(self._view.url.query)
        self.POST = post_data or {}
        self.method = 'POST' if self.POST else 'GET'

        self.server = self._view.server
        self.client = Client(self._view)
        self.route = self._view.route
        self.match_info = self._view.match_info
