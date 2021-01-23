from lona.views import handle_500 as _handle_500


def handle_500(request, exception):
    if request.url.path == '/crashes/handle-500/':
        raise ValueError('Success! This should crash!')

    return _handle_500(request, exception)
