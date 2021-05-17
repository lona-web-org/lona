from lona.view import LonaView


class NonInteractiveView(LonaView):
    def handle_request(self, request):
        return """
            <h2>Non Interactive View</h2>
            <a href="/">Home</a>
        """
