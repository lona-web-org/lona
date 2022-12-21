from lona.view import View


class JSONResponseView(View):
    def handle_request(self, request):
        return {
            'json': {'foo': 'bar'},
        }
