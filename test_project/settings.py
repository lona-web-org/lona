import traceback
import html
import sys

MAX_WORKER_THREADS = 4
MAX_RUNTIME_THREADS = 3
MAX_APPLICATION_THREADS = 0

ROUTING_TABLE = 'routes.py::routes'

STATIC_DIRS = [
    'static',
]

TEMPLATE_DIRS = [
    'templates',
]

TEMPLATE_EXTRA_FILTERS = {
    'custom_reverse': lambda string: string[::-1],
}

MIDDLEWARES = [
    'middlewares.py::CrashingMiddleware',
    'middlewares.py::PermissionMiddleware',
]

ERROR_404_VIEW = 'views/error_404.py::Error404View'
ERROR_500_VIEW = 'views/error_500.py::Error500View'


# template context ############################################################
def format_exception(exception):
    if sys.version_info >= (3, 10):
        lines = traceback.format_exception(exception)

    else:
        lines = traceback.format_exception(
            etype=type(exception),
            value=exception,
            tb=exception.__traceback__,
        )

    return ''.join(lines)


TEMPLATE_EXTRA_CONTEXT = {
    'extra_context_variable': 'bar',
    'format_exception': format_exception,
    'html_escape': html.escape,
}
