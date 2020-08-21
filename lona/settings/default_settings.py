import os

# routing
ROUTING_TABLE = 'lona.settings.default_routes.routes'

# templating
CORE_TEMPLATE_DIRS = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
]

TEMPLATE_DIRS = []

FRONTEND_TEMPLATE = 'lona/frontend.html'
NOT_FOUND_404_TEMPLATE = 'lona/404.html'
INTERNAL_ERROR_500_TEMPLATE = 'lona/500.html'

# static files
CORE_STATIC_DIRS = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
]

STATIC_DIRS = []
STATIC_URL_PREFIX = '/static/'

# views
FRONTEND_VIEW = 'lona.views.frontend'
NOT_FOUND_404_VIEW = 'lona.views.not_found_404'
INTERNAL_ERROR_500_TEMPLATE = 'lona.views.internal_error_500'
VIEW_CACHING = True
VIEW_CACHE_PRELOAD = False

# middlewares
CORE_WEBSOCKET_MIDDLEWARES = [
    'lona.middlewares.websocket_middlewares.json_middleware',
    'lona.middlewares.websocket_middlewares.lona_message_middleware',
]

WEBSOCKET_MIDDLEWARES = []

# debugger
# TODO: make configurable
DEBUG = True
DEBUGGER_ROUTING_TABLE = 'lona.debugger.routes.routes'
DEBUGGER_FRONTEND_VIEW = 'lona.debugger.views.frontend'

CORE_TEMPLATE_DIRS.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'debugger/templates')
)

CORE_STATIC_DIRS.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'debugger/static')
)
