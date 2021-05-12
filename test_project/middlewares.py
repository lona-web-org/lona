class CrashingMiddleware:
    def handle_connection(self, data):
        request = data.request

        if request.path == '/crashes/handle-connection/':
            raise ValueError('It worked! This should crash!')

        return data

    def handle_request(self, data):
        request = data.request

        if request.url.path == '/crashes/handle-request/':
            raise ValueError('It worked! This should crash!')

        return data


class RateLimitMiddleware:
    VIEW_MAX = 2

    def handle_request(self, data):
        request = data.request
        user = request.user

        if request.server.get_running_views_count(user) < (self.VIEW_MAX + 1):
            return data

        return 'To many running views'
