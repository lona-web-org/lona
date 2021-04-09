from lona.view import LonaView


class InteractiveErrorView(LonaView):
    def handle_request(self, request):
        return str(1 / 0)
