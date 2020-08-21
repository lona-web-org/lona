class NotInteractiveError(Exception):
    pass


class Connection:
    def __init__(self, server, http_request, websocket=None):
        self.server = server
        self.http_request = http_request
        self.websocket = websocket

        self.user = None

    @property
    def is_interactive(self):
        return self.websocket is not None

    def send_str(self, string):
        if not self.is_interactive:
            raise NotInteractiveError

        # TODO error handling (disconnects, reconnects, etc.)

        self.server.run_coroutine_sync(self.websocket.send_str(string))
