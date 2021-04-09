from lona.view import LonaView


class FrontendView(LonaView):
    def handle_request(self, request):
        return {
            'template': request.server.settings.FRONTEND_TEMPLATE,
            'request': request,
        }


class Error403View(LonaView):
    def handle_request(self, request):
        return {
            'template': request.server.settings.ERROR_403_TEMPLATE,
            'request': request,
        }


class Error404View(LonaView):
    def handle_request(self, request):
        return {
            'template': request.server.settings.ERROR_404_TEMPLATE,
            'request': request,
        }


class Error500View(LonaView):
    def handle_request(self, request, exception):
        return {
            'template': request.server.settings.ERROR_500_TEMPLATE,
            'request': request,
            'exception': exception,
        }
