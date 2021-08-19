import os

MAX_WORKER_THREADS = 4
MAX_STATIC_THREADS = 4
MAX_RUNTIME_THREADS = 6

# routing
ROUTING_TABLE = 'lona.default_routes.routes'
ROUTING_RESOLVE_CACHE_MAX_SIZE = 1000
ROUTING_REVERSE_CACHE_MAX_SIZE = 1000

# templating
CORE_TEMPLATE_DIRS = [
    os.path.join(os.path.dirname(__file__), 'templates'),
]

TEMPLATE_DIRS = []

FRONTEND_TEMPLATE = 'lona/frontend.html'
ERROR_403_TEMPLATE = 'lona/403.html'
ERROR_404_TEMPLATE = 'lona/404.html'
ERROR_500_TEMPLATE = 'lona/500.html'

TEMPLATE_EXTRA_CONTEXT = {}

# static files
CORE_STATIC_DIRS = [
    os.path.join(os.path.dirname(__file__), 'static'),
]

STATIC_DIRS = []
STATIC_URL_PREFIX = '/static/'
STATIC_FILES_SERVE = True
STATIC_FILES_STYLE_TAGS_TEMPLATE = 'lona/style_tags.html'
STATIC_FILES_SCRIPT_TAGS_TEMPLATE = 'lona/script_tags.html'
STATIC_FILES_ENABLED = []
STATIC_FILES_DISABLED = []
STATIC_FILES_CLIENT_URL = '/lona/lona.js'

# client
CLIENT_RECOMPILE = False
CLIENT_VIEW_START_TIMEOUT = 2
CLIENT_INPUT_EVENT_TIMEOUT = 2

# sessions
SESSIONS = True
SESSIONS_KEY_GENERATOR = 'lona.middlewares.sessions.generate_session_key'
SESSIONS_KEY_NAME = 'sessionid'
SESSIONS_KEY_RANDOM_LENGTH = 28

# views
CORE_FRONTEND_VIEW = 'lona.default_views.FrontendView'
FRONTEND_VIEW = ''

# error views
CORE_ERROR_403_VIEW = 'lona.default_views.Error403View'
CORE_ERROR_404_VIEW = 'lona.default_views.Error404View'
CORE_ERROR_500_VIEW = 'lona.default_views.Error500View'

ERROR_403_VIEW = ''
ERROR_404_VIEW = ''
ERROR_500_VIEW = ''

# middlewares
CORE_MIDDLEWARES = [
    'lona.middlewares.sessions.LonaSessionMiddleware',
    'lona.middlewares.lona_messages.LonaMessageMiddleware',
]

MIDDLEWARES = []

# shell
CORE_COMMANDS = [
    'lona.shell.commands.lona_server_state.LonaServerStateCommand',
    'lona.shell.commands.lona_static_files.LonaStaticFilesCommand',
    'lona.shell.commands.lona_connections.LonaConnectionsCommand',
    'lona.shell.commands.lona_middlewares.LonaMiddlewaresCommand',
    'lona.shell.commands.lona_templates.LonaTemplatesCommand',
    'lona.shell.commands.lona_settings.LonaSettingsCommand',
    'lona.shell.commands.lona_routes.LonaRoutesCommand',
    'lona.shell.commands.lona_views.LonaViewsCommand',
    'lona.shell.commands.lona_info.LonaInfoCommand',
]

COMMANDS = []

# testing
TEST_VIEW_START_TIMEOUT = False
TEST_INPUT_EVENT_TIMEOUT = False
