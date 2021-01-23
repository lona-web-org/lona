import traceback

from lona.views import handle_500 as _handle_500


def handle_500(request, exception):
    if request.url.path == '/crashes/handle-500/':
        raise ValueError('Success! This should crash!')

    if not request.user.is_authenticated:
        return _handle_500(request, exception)

    exception_string = ''.join(
        traceback.format_exception(
            etype=type(exception),
            value=exception,
            tb=exception.__traceback__,
        )
    )

    return """
        <h1>500</h1>
        <pre>{}</pre>
    """.format(
        exception_string,
    )
