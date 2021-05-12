import asyncio
import logging

from aiohttp import ClientConnectorError, ClientSession, WSMsgType

from lona.message_bus.protocol import decode_message, encode_message

logger = logging.getLogger('lona.message_bus.client')


class MessageBusClient:
    def __init__(self, server):
        self.server = server

        self.session = None
        self.websocket = None
        self._running = True

        self.url = self.server.render_string(
            self.server.settings.MESSAGE_CLIENT_URL,
            {
                'server': self.server,
                'settings': self.server.settings,
            },
        )

        self.issuer = self.server.render_string(
            self.server.settings.MESSAGE_CLIENT_ISSUER,
            {
                'server': self.server,
                'settings': self.server.settings,
            },
        )

    def handle_message(self, raw_message):
        logger.debug('raw message received: %s', repr(raw_message))

        message_is_valid, message = decode_message(raw_message)

        if not message_is_valid:
            logger.warning('invalid message skipped: %s', repr(raw_message))

            return

        self.server.middleware_controller.handle_bus_message(
            issuer=message[0],
            topic=message[1],
            params=message[2],
        )

    async def _receive_messages(self):
        self.session = ClientSession()

        while self._running:
            try:
                logger.debug('connecting to %s', self.url)

                self.websocket = await self.session.ws_connect(self.url)

                logger.debug('connected')

                async for message in self.websocket:
                    if message.type == WSMsgType.TEXT:
                        self.server.run_function_async(
                            self.handle_message,
                            message.data,
                        )

                    elif message.type == WSMsgType.PING:
                        await self.websocket.pong()

                    elif message.type in (WSMsgType.CLOSED, WSMsgType.ERROR):
                        await self.websocket.close()

            except asyncio.CancelledError:
                logger.debug('CancelledError')

                return

            except ClientConnectorError:
                logger.error('ConnectionRefusedError: {}'.format(self.url))

            except Exception:
                logger.error(
                    'exception raised',
                    exc_info=True,
                )

            logger.debug('disconnected')

            if self._running:
                logger.debug(
                    'retrying in %ss',
                    self.server.settings.MESSAGE_CLIENT_RETRY_INTERVAL,
                )

                await asyncio.sleep(
                    self.server.settings.MESSAGE_CLIENT_RETRY_INTERVAL,
                )

            else:
                logger.debug('shutting down')

    async def start(self):
        if not self.server.settings.MESSAGE_CLIENT:
            logger.debug('message client disabled')

            return

        logger.debug('start')

        self._running = True
        self.server.loop.create_task(self._receive_messages())

    async def stop(self):
        if not self.server.settings.MESSAGE_CLIENT:
            return

        self._running = False

        if self.session is not None:
            await self.session.close()

        if self.websocket is not None:
            await self.websocket.close()

        logger.debug('stop')

    def send_str(self, string, sync=True):
        try:
            return self.server.run(
                self.websocket.send_str(string),
                sync=sync,
            )

        except ConnectionResetError:
            # this exception gets handled by aiohttp internally and
            # can be ignored

            pass

        except Exception:
            logger.error(
                'exception raised while sending message',
                exc_info=True,
            )

    def send_message(self, topic, issuer=None, params=None):
        issuer = issuer or self.issuer

        message = encode_message(
            issuer=issuer,
            topic=topic,
            params=params,
        )

        self.send_str(message)
