class NotInteractiveError(Exception):
    pass


class Connection:
    def __init__(self, server, http_request, websocket=None):
        self.server = server
        self.http_request = http_request
        self.websocket = websocket

    @property
    def interactive(self):
        return self.websocket is not None

    @property
    def user(self):
        return getattr(self, '_user', None)

    @user.setter
    def user(self, value):
        self._user = value

    def send_str(self, string, wait=True):
        if not self.interactive:
            raise NotInteractiveError

        try:
            return self.server.run_coroutine_sync(
                self.websocket.send_str(string),
                wait=wait,
            )

        except ConnectionResetError:
            # this exception gets handled by aiohttp internally and
            # can be ignored

            pass

    async def close(self):
        if not self.interactive:
            raise NotInteractiveError

        await self.websocket.close()
