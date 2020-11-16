from aiohttp.web import Response


def handle_request(request):
    return Response(
        body='<h1>Pass Through View</h1>',
        content_type='text/html',
    )
