import logging

from lona.errors import ForbiddenError

logger = logging.getLogger('test_project')


class CrashingMiddleware:
    async def on_startup(self, data):
        logger.debug('running startup hook')

    async def on_shutdown(self, data):
        logger.debug('running shutdown hook')

    def handle_connection(self, data):
        http_request = data.http_request

        if http_request.path == '/crashes/handle-connection/':
            raise ValueError('It worked! This should crash!')

        return data

    def handle_request(self, data):
        request = data.request

        if request.url.path == '/crashes/handle-request/':
            raise ValueError('It worked! This should crash!')

        return data


class PermissionMiddleware:
    def handle_request(self, data):
        request = data.request

        paths = (
            '/permissions/access-denied-in-PermissionMiddleware/',
            '/permissions/access-denied-in-PermissionMiddleware/non-interactive/',
        )

        if request.url.path in paths:
            raise ForbiddenError

        return data


class RateLimitMiddleware:
    VIEW_MAX = 2

    def handle_request(self, data):
        request = data.request
        user = request.user

        if request.server.get_running_views_count(user) < (self.VIEW_MAX + 1):
            return data

        return 'To many running views'
