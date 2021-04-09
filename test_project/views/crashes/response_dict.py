from lona.view import LonaView


class ResponseDictView(LonaView):
    def handle_request(self, request):
        return {
            'template_string': 'foo',
            'template': 'bar',
        }
