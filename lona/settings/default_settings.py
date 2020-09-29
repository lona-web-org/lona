import os

# routing
ROUTING_TABLE = 'lona.settings.default_routes.routes'

# templating
CORE_TEMPLATE_DIRS = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
]

TEMPLATE_DIRS = []

FRONTEND_TEMPLATE = 'lona/frontend.html'
ERROR_404_TEMPLATE = 'lona/404.html'
ERROR_500_TEMPLATE = 'lona/500.html'

# static files
CORE_STATIC_DIRS = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
]

STATIC_DIRS = []
STATIC_URL_PREFIX = '/static/'

# views
FRONTEND_VIEW = 'lona.views.frontend'
VIEW_CACHING = True
VIEW_CACHE_PRELOAD = False

# error handler
ERROR_404_HANDLER = 'lona.views.handle_404'
ERROR_500_HANDLER = 'lona.views.handle_500'
ERROR_404_FALLBACK_HANDLER = 'lona.views.handle_404'
ERROR_500_FALLBACK_HANDLER = 'lona.views.handle_500'

# websocket middlewares
CORE_WEBSOCKET_MIDDLEWARES = [
    'lona.middlewares.websocket_middlewares.json_middleware',
    'lona.middlewares.websocket_middlewares.lona_message_middleware',
]

WEBSOCKET_MIDDLEWARES = []

# request middlewares
REQUEST_MIDDLEWARES = [
    'lona.middlewares.request_middlewares.lona_session_middleware',
]

# scheduling
TASK_ZONES = [
    ('service',         5),

    ('system-high',    10),
    ('system-medium',   5),
    ('system-low',      2),

    ('high',           10),
    ('medium',          5),
    ('low',             2),
]

THREAD_ZONES = [
    ('service',         5),

    ('system-high',    10),
    ('system-medium',   5),
    ('system-low',      2),

    ('high',           10),
    ('medium',          5),
    ('low',             2),
]

DEFAULT_TASK_ZONE = 'medium'
DEFAULT_THREAD_ZONE = 'medium'

ROUTING_PRIORITY = 'system-high'
HTTP_REQUEST_PRIORITY = 'system-medium'
STATIC_REQUEST_PRIORITY = 'system-low'
CONNECTION_MIDDLEWARE_PRIORITY = 'system-medium'
WEBSOCKET_MIDDLEWARE_PRIORITY = 'system-medium'
REQUEST_MIDDLEWARE_PRIORITY = 'system-medium'
FRONTEND_VIEW_PRIORITY = 'system-high'
SHUTDOWN_PRIORITY = 'system-high'

DEFAULT_MULTI_USER_VIEW_PRIORITY = 'service'
DEFAULT_VIEW_PRIORITY = 'medium'

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
