from lona.view import View


class NonInteractiveErrorView(View):
    def handle_request(self, request):
        return str(1 / 0)
