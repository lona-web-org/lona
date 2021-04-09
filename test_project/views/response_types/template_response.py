from lona.view import LonaView


class TemplateResponseView(LonaView):
    def handle_request(self, request):
        return {
            'template': 'template_response.html',
            'test_variable': 'foo',
        }
