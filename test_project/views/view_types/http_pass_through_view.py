from lona.view import LonaView

from aiohttp.web import Response


class HTTPPassThroughView(LonaView):
    def handle_request(self, request):
        return Response(
            body="""
                <h2>Pass Through View</h2>
                <a href="/">Home</a>
            """,
            content_type='text/html',
        )
