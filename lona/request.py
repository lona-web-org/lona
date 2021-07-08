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

    @property
    def user(self):
        return getattr(self.connection, 'user', None)

    @property
    def frontend(self):
        return self._view_runtime.frontend

    @property
    def server(self):
        return self._view_runtime.server

    @property
    def route(self):
        return self._view_runtime.route

    @property
    def match_info(self):
        return self._view_runtime.match_info
