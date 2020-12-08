import os

# debugger
if DEBUG:  # NOQA
    DEBUGGER_ROUTING_TABLE = 'lona.debugger.routes.routes'
    DEBUGGER_FRONTEND_VIEW = 'lona.debugger.views.frontend'

    CORE_TEMPLATE_DIRS.insert(  # NOQA
        0,
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'debugger/templates')
    )

    CORE_STATIC_DIRS.insert(  # NOQA
        0,
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'debugger/static')
    )
