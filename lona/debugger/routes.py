from lona.routing import Route

FRONTEND_VIEW = 'lona.debugger.views.frontend'

routes = [
    Route(
        '/debugger/view_controller(/)',
        'lona.debugger.views.ViewControllerDashboard',
        frontend_view=FRONTEND_VIEW,
    ),
    Route(
        '/debugger(/)',
        'lona.debugger.views.index',
        frontend_view=FRONTEND_VIEW,
    ),
]
