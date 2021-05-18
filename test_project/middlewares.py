class CrashingMiddleware:
    def process_connection(self, data):
        request = data.request

        if request.path == '/crashes/process-connection/':
            raise ValueError('It worked! This should crash!')

        return data

    def process_request(self, data):
        request = data.request

        if request.url.path == '/crashes/process-request/':
            raise ValueError('It worked! This should crash!')

        return data


class RateLimitMiddleware:
    VIEW_MAX = 2

    def process_request(self, data):
        request = data.request
        user = request.user

        if request.server.get_running_views_count(user) < (self.VIEW_MAX + 1):
            return data

        return 'To many running views'
