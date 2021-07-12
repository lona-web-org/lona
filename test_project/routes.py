import os

from lona.routing import Route, MATCH_ALL

DJANGO = False

if os.environ.get('DJANGO', '0') == '1':
    from django_project.wsgi import application
    from aiohttp_wsgi import WSGIHandler

    DJANGO = True
    wsgi_handler = WSGIHandler(application)


routes = [
    # view types
    Route('/view-types/interactive-view/',
          'views/view_types/interactive_view.py::InteractiveView'),

    Route('/view-types/non-interactive-view/',
          'views/view_types/non_interactive_view.py::NonInteractiveView',
          interactive=False),

    Route('/view-types/http-pass-through/',
          'views/view_types/http_pass_through_view.py::HTTPPassThroughView',
          http_pass_through=True),

    Route('/view-types/daemonized-view/<name>/',
          'views/view_types/daemonized_view.py::DaemonizedView'),

    Route('/view-types/daemonized-view/',
          'views/view_types/daemonized_view.py::DaemonizedView'),

    Route('/view-types/async-view/',
          'views/view_types/async_view.py::AsyncView'),

    # response types
    Route('/response-types/template-response/',
          'views/response_types/template_response.py::TemplateResponseView'),

    Route('/response-types/file-response/',
          'views/response_types/file_response.py::FileResponseView',
          interactive=False),

    Route('/response-types/json-response/',
          'views/response_types/json_response.py::JSONResponseView',
          interactive=False),

    Route('/response-types/redirect/',
          'views/response_types/redirect.py::RedirectView'),

    Route('/response-types/http-redirect/',
          'views/response_types/http_redirect.py::HTTPRedirectView'),

    # permissions
    Route('/permissions/access-denied-in-PermissionMiddleware/',
          'views/permissions/denied_in_middleware.py::View'),

    Route('/permissions/access-denied-in-PermissionMiddleware/non-interactive/',  # NOQA
          'views/permissions/denied_in_middleware.py::View',
          interactive=False),

    Route('/permissions/access-denied-in-handle-request/',
          'views/permissions/denied_in_handle_request.py::DenyAccess'),

    Route('/permissions/access-denied-in-handle-request/non-interactive/',
          'views/permissions/denied_in_handle_request.py::DenyAccess',
          interactive=False),

    # error types
    Route('/error-types/interactive-500/',
          'views/error_types/interactive_500.py::InteractiveErrorView'),

    Route('/error-types/non-interactive-500/',
          'views/error_types/non_interactive_500.py::NonInteractiveErrorView',
          interactive=False),

    Route(
        '/error-types/non-interactive-feature-error/',
        'views/error_types/non_interactive_feature_error.py::NonInteractiveFeatureErrorView',  # NOQA
    ),

    # crashes
    Route('/crashes/handle-connection/',
          'views/crashes/middlewares.py::UnreachableView'),

    Route('/crashes/handle-request/',
          'views/crashes/middlewares.py::UnreachableView'),

    Route('/crashes/response-dict/',
          'views/crashes/response_dict.py::ResponseDictView'),

    Route('/crashes/input-events/',
          'views/crashes/input_events.py::CrashingEventHandler'),

    Route('/crashes/handle-500/',
          'views/crashes/handle_500.py::CrashingView'),

    # routing
    Route('/routing/url-args/<a:[^/]+>/<b:[^/]+>/<c:[^/]+>/',
          'views/routing/url_args.py::URLArgsView'),

    # events
    Route('/events/click-events/',
          'views/events/click_events.py::ClickEventView'),

    Route('/events/change-events/',
          'views/events/change_events.py::ChangeEventsView'),

    Route('/events/non-node-events/',
          'views/events/non_node_events.py::NonNodeEventView'),

    Route('/events/widget-event-handler/',
          'views/events/widget_event_handler.py::WidgetEventHandlerView'),

    Route('/events/class-based-view/',
          'views/events/class_based_view.py::ClassBasedView'),

    Route('/events/event-bubbling/',
          'views/events/event_bubbling.py::EventBubblingView'),

    Route('/events/data-binding/',
          'views/events/data_binding.py::DataBindingView'),

    # locking
    Route('/locking/html-tree/',
          'views/locking/html_tree_locking.py::LockingView'),

    Route('/locking/server-state/',
          'views/locking/server_state_locking.py::LockingView'),

    # window actions
    Route('/window-actions/set-title/',
          'views/window_actions/set_title.py::WindowTitleView'),

    # frontend
    Route('/frontend/widget-data/',
          'views/frontend/widget_data.py::WidgetDataView'),

    Route('/frontend/custom-event/',
          'views/frontend/custom_event.py::CustomEventView'),

    Route('/frontend/custom-messages/',
          'views/frontend/custom_messages.py::CustomMessagesView'),

    # contrib
    Route('/contrib/chart-js/',
          'views/contrib/chartjs.py::ChartJSView'),

    # home
    Route('/', 'views/home.py::HomeView'),
]


if DJANGO:
    routes += [
        Route('/django/login-required/',
              'views/django/permission_views.py::DjangLoginView'),

        Route('/django/template-based-form/',
              'views/django/template_based_form.py::DjangoTemplateView'),

        Route('/django/node-based-form/',
              'views/django/node_based_form.py::DjangoNodeBasedView'),

        Route('/django/data-binding-form/',
              'views/django/data_binding_form.py::DjangoDatabindingView'),

        Route(MATCH_ALL, wsgi_handler, http_pass_through=True),
    ]
