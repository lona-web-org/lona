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
    class RateLimitMiddleware:
        VIEW_MAX = 2

        def process_request(self, data):
            request = data.request
            user = request.user

            if request.server.get_running_views_count(user) < self.VIEW_MAX:

                return data

            return 'To many running views'

    MIDDLEWARES = [
        'lona.contrib.django.auth.DjangoSessionMiddleware',
        RateLimitMiddleware,
    ]

HOOKS = {
    'server_stop': [
        'hooks.py::server_stop',
    ],
    'server_start': [
        'hooks.py::server_start'
    ],
}
