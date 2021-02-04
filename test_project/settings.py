import os

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

STARTUP_HOOKS = [
    'hooks.py::server_startup',
]

SHUTDOWN_HOOKS = [
    'hooks.py::server_shutdown',
]

MIDDLEWARES = [
    'middlewares.py::CrashingMiddleware',
]

ERROR_404_HANDLER = 'views/handle_404.py::handle_404'
ERROR_500_HANDLER = 'views/handle_500.py::handle_500'

if os.environ.get('DJANGO', '0') == '1':
    MIDDLEWARES += [
        'lona.contrib.django.auth.DjangoSessionMiddleware',
        'middlewares.py::RateLimitMiddleware',
    ]

    ERROR_500_HANDLER = 'views/django/handle_500.py::handle_500'
