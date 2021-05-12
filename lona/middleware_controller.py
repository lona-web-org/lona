import asyncio
import logging

logger = logging.getLogger('lona.middlewares')


class MiddlewareData:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<MiddlewareData({})>'.format(
            ', '.join(
                ['{}={}'.format(k, repr(v)) for k, v in self.kwargs.items()]
            )
        )


class MiddlewareController:
    HOOK_NAMES = [
        'handle_connection',
        'handle_websocket_message',
        'handle_request',
        'handle_message_bus_connection',
        'handle_bus_message',
    ]

    def __init__(self, server):
        self.server = server

        self.setup()

    def setup(self):
        # setup middlewares
        logger.debug('setup middlewares')

        self.middleware_classes = (
            self.server.settings.CORE_MIDDLEWARES +
            self.server.settings.MIDDLEWARES
        )

        self.middlewares = []

        for i in self.middleware_classes:
            logger.debug('loading %s', i)

            try:
                if isinstance(i, str):
                    middleware_class = self.server.acquire(i)

                else:
                    middleware_class = i

            except Exception:
                logger.error(
                    'Exception raised while loading %s', i, exc_info=True)

            try:
                self.middlewares.append(middleware_class())

            except Exception:
                logger.error(
                    'Exception raised while initializing %s', i, exc_info=True)

        # discover middleware hooks
        logger.debug('discover middleware hooks')

        self.hooks = {
            hook_name: [] for hook_name in self.HOOK_NAMES
        }

        for middleware in self.middlewares:
            logger.debug('discovering %s', middleware)

            for hook_name in self.HOOK_NAMES:
                if not hasattr(middleware, hook_name):
                    continue

                hook = getattr(middleware, hook_name)

                if not callable(hook):
                    continue

                if asyncio.iscoroutinefunction(hook):
                    logger.error(
                        '%s.%s is a coroutine function',
                        middleware,
                        hook_name,
                    )

                self.hooks[hook_name].append(
                    (middleware, hook, ),
                )

                logger.debug('%s.%s discovered', middleware, hook_name)

    def _run_middlewares(self, hook_name, data):
        if hook_name not in self.HOOK_NAMES:
            raise NotImplementedError("unknown hook '{}'".format(hook_name))

        logger.debug(
            'running %s with %s',
            hook_name,
            repr(data),
        )

        for middleware, hook in self.hooks[hook_name]:
            logger.debug(
                'running %s.%s(%s)',
                middleware,
                hook_name,
                repr(data),
            )

            # run middleware hook
            return_value = hook(data)

            if return_value is None:
                # if the middleware does not return the data object it is
                # considered as handled

                logger.debug(
                    'data got handled by %s.%s', middleware, hook_name)

                return True, None, middleware

            elif return_value is not data:
                # if a middleware returns a custom value the data
                # is considered as handled

                logger.debug(
                    'data got handled by %s.%s by returning a custom value: %s',  # NOQA
                    middleware,
                    hook_name,
                    repr(return_value),
                )

                return True, return_value, middleware

        logger.debug('data was not handled')

        return False, data, None

    async def handle_connection(self, connection):
        data = MiddlewareData(
            server=self.server,
            connection=connection,
            request=connection.http_request,
        )

        return await self.server.run_function_async(
            self._run_middlewares,
            'handle_connection',
            data,
        )

    async def handle_websocket_message(self, connection, message):
        data = MiddlewareData(
            server=self.server,
            connection=connection,
            message=message,
        )

        return await self.server.run_function_async(
            self._run_middlewares,
            'handle_websocket_message',
            data,
        )

    def handle_request(self, request, view):
        data = MiddlewareData(
            server=self.server,
            connection=request.connection,
            request=request,
            view=view,
        )

        return self._run_middlewares('handle_request', data)

    async def handle_message_bus_connection(self, connection):
        data = MiddlewareData(
            connection=connection,
        )

        return await self.server.run_function_async(
            self._run_middlewares,
            'handle_message_bus_connection',
            data,
        )

    def handle_bus_message(self, issuer, topic, params):
        data = MiddlewareData(
            issuer=issuer,
            topic=topic,
            params=params,
        )

        return self._run_middlewares('handle_bus_message', data)
