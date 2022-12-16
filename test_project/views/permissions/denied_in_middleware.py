from lona.view import View


class View(View):
    def handle_request(self, request):
        return 'ERROR: This view should not be accessible'
