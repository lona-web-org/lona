from lona.view import LonaView


class JSONResponseView(LonaView):
    def handle_request(self, request):
        return {
            'json': {'foo': 'bar'},
        }
