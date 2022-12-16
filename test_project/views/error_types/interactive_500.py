from lona.view import View


class InteractiveErrorView(View):
    def handle_request(self, request):
        return str(1 / 0)
