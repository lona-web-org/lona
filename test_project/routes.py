from lona.routing import Route

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

    Route('/view-types/form-view/',
          'views/view_types/form_view.py::FormView'),

    Route('/view-types/async-view/',
          'views/view_types/async_view.py::AsyncView'),

    # dict responses
    # interactive
    Route('/dict-responses/interactive/',
          'views/responses/interactive_dict.py::InteractiveView'),

    # non-interactive
    Route('/dict-responses/non-interactive/',
          'views/responses/non_interactive_dict.py::NonInteractiveView'),

    Route('/dict-responses/non-interactive/empty-response',
          'views/responses/non_interactive_dict.py::EmptyResponseView',
          interactive=False),

    Route('/dict-responses/non-interactive/node-response',
          'views/responses/non_interactive_dict.py::NodeResponseView',
          interactive=False),

    Route('/dict-responses/non-interactive/string-response',
          'views/responses/non_interactive_dict.py::StringResponseView',
          interactive=False),

    Route('/dict-responses/non-interactive/template-response',
          'views/responses/non_interactive_dict.py::TemplateResponseView',
          interactive=False),

    Route('/dict-responses/non-interactive/template-string-response',
          'views/responses/non_interactive_dict.py::TemplateStringResponseView',
          interactive=False),

    Route('/dict-responses/non-interactive/redirect-response',
          'views/responses/non_interactive_dict.py::RedirectResponseView',
          interactive=False),

    Route('/dict-responses/non-interactive/http-redirect-response',
          'views/responses/non_interactive_dict.py::HttpRedirectResponseView',
          interactive=False),

    Route('/dict-responses/non-interactive/file-response',
          'views/responses/non_interactive_dict.py::FileResponseView',
          interactive=False),

    Route('/dict-responses/non-interactive/json-response',
          'views/responses/non_interactive_dict.py::JsonResponseView',
          interactive=False),

    Route('/dict-responses/non-interactive/binary-response',
          'views/responses/non_interactive_dict.py::BinaryResponseView',
          interactive=False),

    Route('/dict-responses/non-interactive/custom-headers-response',
          'views/responses/non_interactive_dict.py::CustomHeadersResponseView',
          interactive=False),

    # responses
    # interactive
    Route('/responses/interactive/',
          'views/responses/interactive.py::InteractiveView'),

    # non-interactive
    Route('/responses/non-interactive/',
          'views/responses/non_interactive.py::NonInteractiveView'),

    Route('/responses/non-interactive/empty-response',
          'views/responses/non_interactive.py::EmptyResponseView',
          interactive=False),

    Route('/responses/non-interactive/node-response',
          'views/responses/non_interactive.py::NodeResponseView',
          interactive=False),

    Route('/responses/non-interactive/string-response',
          'views/responses/non_interactive.py::StringResponseView',
          interactive=False),

    Route('/responses/non-interactive/template-response',
          'views/responses/non_interactive.py::TemplateResponseView',
          interactive=False),

    Route('/responses/non-interactive/template-string-response',
          'views/responses/non_interactive.py::TemplateStringResponseView',
          interactive=False),

    Route('/responses/non-interactive/redirect-response',
          'views/responses/non_interactive.py::RedirectResponseView',
          interactive=False),

    Route('/responses/non-interactive/http-redirect-response',
          'views/responses/non_interactive.py::HttpRedirectResponseView',
          interactive=False),

    Route('/responses/non-interactive/file-response',
          'views/responses/non_interactive.py::FileResponseView',
          interactive=False),

    Route('/responses/non-interactive/json-response',
          'views/responses/non_interactive.py::JsonResponseView',
          interactive=False),

    Route('/responses/non-interactive/binary-response',
          'views/responses/non_interactive.py::BinaryResponseView',
          interactive=False),

    Route('/responses/non-interactive/custom-headers-response',
          'views/responses/non_interactive.py::CustomHeadersResponseView',
          interactive=False),

    # permissions
    Route('/permissions/access-denied-in-PermissionMiddleware/',
          'views/permissions/denied_in_middleware.py::View'),

    Route('/permissions/access-denied-in-PermissionMiddleware/non-interactive/',
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
        'views/error_types/non_interactive_feature_error.py::NonInteractiveFeatureErrorView',
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

    Route('/crashes/widget/',
          'views/crashes/widget.py::CrashingWidgetView'),

    # routing
    Route('/routing/url-args/<a:[^/]+>/<b:[^/]+>/<c:[^/]+>/',
          'views/routing/url_args.py::URLArgsView'),

    # events
    Route('/events/click-events/',
          'views/events/click_events.py::ClickEventView'),

    Route('/events/change-events/',
          'views/events/change_events.py::ChangeEventsView'),

    Route('/events/focus-events/',
          'views/events/focus_events.py::FocusEventsView'),

    Route('/events/blur-events/',
          'views/events/blur_events.py::BlurEventsView'),

    Route('/events/non-node-events/',
          'views/events/non_node_events.py::NonNodeEventView'),

    Route('/events/node-event-handler/',
          'views/events/node_event_handler.py::NodeEventHandlerView'),

    Route('/events/class-based-view/',
          'views/events/class_based_view.py::ClassBasedView'),

    Route('/events/event-bubbling/',
          'views/events/event_bubbling.py::EventBubblingView'),

    Route('/events/data-binding/',
          'views/events/data_binding.py::DataBindingView'),

    Route('/events/callbacks/',
          'views/events/callbacks.py::InputEventCallbackView'),

    # locking
    Route('/locking/html-tree/',
          'views/locking/html_tree_locking.py::LockingView'),

    Route('/locking/server-state/',
          'views/locking/server_state_locking.py::LockingView'),

    # window actions
    Route('/window-actions/set-title/',
          'views/window_actions/set_title.py::WindowTitleView'),

    # frontend
    Route('/frontend/static-files/',
          'views/frontend/static_files.py::StaticFilesView'),

    Route('/frontend/rendering/',
          'views/frontend/rendering.py::RenderingTestView'),

    Route('/frontend/custom-event/',
          'views/frontend/custom_event.py::CustomEventView'),

    Route('/frontend/custom-messages/',
          'views/frontend/custom_messages.py::CustomMessagesView'),

    Route('/frontend/redirects<url:.*>',
          'views/frontend/redirects.py::RedirectsView'),

    # home
    Route('/', 'views/home.py::HomeView'),
]
