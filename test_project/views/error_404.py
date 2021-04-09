from lona.default_views import Error404View as _Error404View


class Error404View(_Error404View):
    def handle_request(self, request):
        if request.url.path == '/crashes/handle-404/':
            raise ValueError('Success! This should crash!')

        return super().handle_request(request)
