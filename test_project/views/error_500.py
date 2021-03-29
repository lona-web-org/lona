from lona.views import Error500View as _Error500View


class Error500View(_Error500View):
    def handle_request(self, request, exception):
        if request.url.path == '/crashes/handle-500/':
            raise ValueError('Success! This should crash!')

        return super().handle_request(request, exception)
