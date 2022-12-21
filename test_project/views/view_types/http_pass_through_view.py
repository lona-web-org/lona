from aiohttp.web import Response

from lona.view import View


class HTTPPassThroughView(View):
    def handle_request(self, request):
        return Response(
            body="""
                <h2>Pass Through View</h2>
                <a href="/">Home</a>
            """,
            content_type='text/html',
        )
