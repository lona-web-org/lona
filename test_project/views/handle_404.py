from lona.views import handle_404 as _handle_404


def handle_404(request):
    if request.url.path == '/crashes/handle-404/':
        raise ValueError('Success! This should crash!')

    return _handle_404(request)
