from __future__ import annotations

from typing import Callable, Any
import os

MAX_WORKER_THREADS = 4
MAX_STATIC_THREADS = 4
MAX_RUNTIME_THREADS = 6

# routing
ROUTING_TABLE = 'lona.default_routes.routes'
ROUTING_NAME_CACHE_MAX_SIZE = 1000
ROUTING_RESOLVE_CACHE_MAX_SIZE = 1000
ROUTING_REVERSE_CACHE_MAX_SIZE = 1000

# templating
CORE_TEMPLATE_DIRS = [
    os.path.join(os.path.dirname(__file__), 'templates'),
]

TEMPLATE_DIRS: list[str] = []

FRONTEND_TEMPLATE = 'lona/frontend.html'
ERROR_403_TEMPLATE = 'lona/403.html'
ERROR_404_TEMPLATE = 'lona/404.html'
ERROR_500_TEMPLATE = 'lona/500.html'

TEMPLATE_EXTRA_CONTEXT: dict[str, Any] = {}
TEMPLATE_EXTRA_FILTERS: dict[str, Callable] = {}

# static files
CORE_STATIC_DIRS = [
    os.path.join(os.path.dirname(__file__), 'static'),
]

STATIC_DIRS: list[str] = []
STATIC_URL_PREFIX = '/static/'
STATIC_FILES_SERVE = True
STATIC_FILES_STYLE_TAGS_TEMPLATE = 'lona/style_tags.html'
STATIC_FILES_SCRIPT_TAGS_TEMPLATE = 'lona/script_tags.html'
STATIC_FILES_ENABLED: list[str] = []
STATIC_FILES_DISABLED: list[str] = []

# client
CLIENT_DEBUG = False
CLIENT_VIEW_START_TIMEOUT = 2
CLIENT_INPUT_EVENT_TIMEOUT = 2
CLIENT_PING_INTERVAL = 60


# sessions
SESSIONS = True
SESSIONS_KEY_GENERATOR = 'lona.middlewares.sessions.generate_session_key'
SESSIONS_KEY_NAME = 'sessionid'
SESSIONS_KEY_RANDOM_LENGTH = 28

# views
CORE_FRONTEND_VIEW = 'lona.default_views.FrontendView'
FRONTEND_VIEW = ''
INITIAL_SERVER_STATE: dict = {}

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

MIDDLEWARES: list[str] = []

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

COMMANDS: list[str] = []

# testing
TEST_VIEW_START_TIMEOUT = False
TEST_INPUT_EVENT_TIMEOUT = False

# server
AIOHTTP_CLIENT_MAX_SIZE = 1024**2
