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

if os.environ.get('DJANGO', '0') == '1':
    MIDDLEWARES = [
        'lona.contrib.django.auth.DjangoSessionMiddleware',
    ]
