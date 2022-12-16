from lona.view import View


class NonInteractiveView(View):
    def handle_request(self, request):
        return """
            <h2>Non Interactive View</h2>
            <a href="/">Home</a>
        """
