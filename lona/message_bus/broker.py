import logging
import asyncio

from aiohttp.web import WebSocketResponse, Response
from aiohttp import WSMsgType

from lona.message_bus.protocol import decode_message
from lona.connection import Connection

logger = logging.getLogger('lona.message_bus.broker')


class MessageBusBroker:
    def __init__(self, server):
        self.server = server

        self.connections = []

    async def stop(self, *args, **kwargs):
        logger.debug('stop')

        for connection in self.connections.copy():
            try:
                await connection.close()

            except Exception:
                pass

    async def broadcast(self, raw_message):
        counter = 0

        for connection in self.connections.copy():
            try:
                await connection.send_str(raw_message, sync=False)
                counter += 1

            except ConnectionResetError:
                # this exception gets handled by aiohttp internally and
                # can be ignored

                pass

        logger.debug(
            'message %s broadcasted to %s clients',
            repr(raw_message),
            counter,
        )

    def handle_websocket_message(self, raw_message):
        logger.debug('raw message received: %s', repr(raw_message))

        message_is_valid, message = decode_message(raw_message)

        if not message_is_valid:
            logger.warning('invalid message skipped: %s', repr(raw_message))

            return

        self.server.run_coroutine_sync(
            self.broadcast(raw_message),
            wait=False,
        )

    async def handle_websocket_request(self, http_request):
        # setup websocket
        websocket = WebSocketResponse()
        await websocket.prepare(http_request)

        logger.debug('client %s: connected', hex(id(websocket)))

        connection = Connection(
            server=self.server,
            http_request=http_request,
            websocket=websocket,
        )

        # run middlewares
        middleware_controller = self.server.middleware_controller

        handled, message, middleware = \
            await middleware_controller.handle_message_bus_connection(
                connection=connection,
            )

        # connection got rejected
        if handled:
            logger.debug(
                'client %s: connection rejected by %s',
                hex(id(websocket)),
                repr(middleware),
            )

            if isinstance(message, str):
                try:
                    await connection.send_str(message, sync=False)

                except Exception:
                    pass

            await connection.close()

            return websocket

        # main loop
        self.connections.append(connection)

        try:
            async for message in websocket:
                if message.type == WSMsgType.TEXT:
                    self.server.run_function_async(
                        self.handle_websocket_message,
                        message.data,
                    )

                elif message.type == WSMsgType.PING:
                    await websocket.pong()

                elif message.type in (WSMsgType.CLOSED, WSMsgType.ERROR):
                    break

        except asyncio.CancelledError:
            logger.debug('CancelledError')

        finally:
            logger.debug('client %s disconnected', id(websocket))

            await websocket.close()

            if connection in self.connections:
                self.connections.remove(connection)

        return websocket

    async def handle_http_request(self, http_request):
        if(http_request.method == 'GET' and
           http_request.headers.get('upgrade', '').lower() == 'websocket'):

            return await self.handle_websocket_request(http_request)

        return Response(
            status=405,
            text='405: Method Not Allowed',
        )
