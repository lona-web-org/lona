import os

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

TEMPLATE_EXTRA_CONTEXT = {
    'extra_context_variable': 'bar',
}

MIDDLEWARES = [
    'middlewares.py::CrashingMiddleware',
    'middlewares.py::PermissionMiddleware',
]

ERROR_404_VIEW = 'views/error_404.py::Error404View'
ERROR_500_VIEW = 'views/error_500.py::Error500View'

if os.environ.get('DJANGO', '0') == '1':
    MIDDLEWARES += [
        'lona.contrib.django.auth.DjangoSessionMiddleware',
        'middlewares.py::RateLimitMiddleware',
    ]

    ERROR_500_VIEW = 'views/django/error_500.py::Error500View'
