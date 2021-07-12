from lona.view import LonaView


class View(LonaView):
    def handle_request(self, request):
        return 'ERROR: This view should not be accessible'
