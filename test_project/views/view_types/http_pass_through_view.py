from lona import LonaView

from aiohttp.web import Response


class HTTPPassThroughView(LonaView):
    def handle_request(self, request):
        return Response(
            body='<h1>Pass Through View</h1>',
            content_type='text/html',
        )
