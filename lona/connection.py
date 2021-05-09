class NotInteractiveError(Exception):
    pass


class Connection:
    def __init__(self, server, http_request, websocket=None):
        self.server = server
        self.http_request = http_request
        self.websocket = websocket

    @property
    def is_interactive(self):
        return self.websocket is not None

    @property
    def user(self):
        return getattr(self, '_user', None)

    @user.setter
    def user(self, value):
        self._user = value

    def send_str(self, string, sync=True):
        if not self.is_interactive:
            raise NotInteractiveError

        try:
            return self.server.run(
                self.websocket.send_str(string),
                sync=sync,
            )

        except ConnectionResetError:
            # this exception gets handled by aiohttp internally and
            # can be ignored

            pass

    async def close(self):
        if not self.is_interactive:
            raise NotInteractiveError

        await self.websocket.close()
