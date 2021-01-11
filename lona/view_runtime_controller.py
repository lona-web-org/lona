import logging

from yarl import URL

from lona.protocol import encode_http_redirect, METHOD
from lona.html.abstract_node import AbstractNode
from lona.view_runtime import ViewRuntime
from lona.exceptions import ServerStop
from lona.imports import acquire
from lona.request import Request
from lona.types import Mapping
from lona.json import dumps

logger = logging.getLogger('lona.view_runtime_controller')


class ViewRuntimeController:
    def __init__(self, server):
        self.server = server

        self.running_single_user_views = Mapping()
        # contains: {
        #     connection.user: [
        #         view_runtime,
        #     ]
        # }

        self.running_multi_user_views = Mapping()
        # contains: {
        #    route: view_runtime,
        # }

    def start(self):
        # TODO: add support for custom view priorities

        # error handler
        logger.debug('loading error handler')

        logger.debug(
            "loading 404 handler from '%s'",
            self.server.settings.ERROR_404_HANDLER,
        )

        self.error_404_handler = acquire(
            self.server.settings.ERROR_404_HANDLER)[1]

        logger.debug(
            "loading 404 fallback handler from '%s'",
            self.server.settings.ERROR_404_FALLBACK_HANDLER,
        )

        self.error_404_fallback_handler = acquire(
            self.server.settings.ERROR_404_FALLBACK_HANDLER)[1]

        logger.debug(
            "loading 500 handler from '%s'",
            self.server.settings.ERROR_500_HANDLER,
        )

        self.error_500_handler = acquire(
            self.server.settings.ERROR_500_HANDLER)[1]

        logger.debug(
            "loading 500 fallback handler from '%s'",
            self.server.settings.ERROR_500_FALLBACK_HANDLER,
        )

        self.error_500_fallback_handler = acquire(
            self.server.settings.ERROR_500_FALLBACK_HANDLER)[1]

        # multi user views
        logger.debug('starting multi user views')

        for route in self.server.router.routes:
            view_runtime = ViewRuntime(
                server=self.server,
                url=None,
                route=route,
                match_info={},
                post_data={},
                frontend=False,
                start_connection=None,
            )

            if view_runtime.view_spec.multi_user:
                logger.debug('starting %s as multi user view',
                             view_runtime.view)

                self.running_multi_user_views[route] = view_runtime

                priority = \
                    self.server.settings.DEFAULT_MULTI_USER_VIEW_PRIORITY

                self.server.schedule(
                    view_runtime.start,
                    priority=priority,
                )

    def stop(self):
        # running views per user
        for user, view_runtimes in self.running_single_user_views.items():
            for view_runtime in view_runtimes:
                view_runtime.stop(reason=ServerStop)

        # multi user views
        for route, view in self.running_multi_user_views.items():
            view.stop(reason=ServerStop)

    # response dicts ##########################################################
    def render_response_dict(self, raw_response_dict, view_name):
        # TODO: warn if keys are ambiguous

        response_dict = {
            'status': 200,
            'content_type': 'text/html',
            'text': '',
            'file': '',
            'redirect': '',
            'http_redirect': '',
        }

        # Node response
        if isinstance(raw_response_dict, AbstractNode):
            response_dict['text'] = str(raw_response_dict)

            return response_dict

        # string response
        if isinstance(raw_response_dict, str):
            logger.debug("'%s' is a string based view", view_name)

            response_dict['text'] = raw_response_dict

            return response_dict

        # find keys
        elif isinstance(raw_response_dict, dict):
            for key in response_dict.keys():
                if key in raw_response_dict:
                    value = raw_response_dict[key]
                    response_dict[key] = value

                    logger.debug(
                        "'%s' sets '%s' to %s", view_name, key, repr(value))

        # redirects
        if 'redirect' in raw_response_dict:
            # TODO: add support for reverse url lookups

            response_dict['redirect'] = raw_response_dict['redirect']

        # http redirect
        elif 'http_redirect' in raw_response_dict:
            # TODO: add support for reverse url lookups

            response_dict['http_redirect'] = raw_response_dict['http_redirect']

        # template response
        elif 'template' in raw_response_dict:
            logger.debug("'%s' is a template view", view_name)

            template_context = raw_response_dict

            if 'context' in template_context:
                template_context = template_context['context']

            response_dict['text'] = \
                self.server.templating_engine.render_template(
                    raw_response_dict['template'],
                    template_context,
                )

        # json response
        elif 'json' in raw_response_dict:
            logger.debug("'%s' is a json view", view_name)

            response_dict['text'] = dumps(raw_response_dict['json'])
            response_dict['content_type'] = 'application/json'

        return response_dict

    # error handler ###########################################################
    def handle_404(self, request):
        try:
            return self.error_404_handler(request)

        except Exception:
            logger.error(
                'Exception occurred while running %s. Falling back to %s',
                self.error_404_handler,
                self.error_404_fallback_handler,
                exc_info=True,
            )

        return self.error_404_fallback_handler(request)

    def handle_500(self, request, exception):
        try:
            return self.error_500_handler(request, exception)

        except Exception:
            logger.error(
                'Exception occurred while running %s. Falling back to %s',
                self.error_500_handler,
                self.error_500_fallback_handler,
                exc_info=True,
            )

        return self.error_500_fallback_handler(request, exception)

    # view management #########################################################
    def remove_connection(self, connection, window_id=None):
        for user, view_runtimes in self.running_single_user_views.items():
            for view_runtime in view_runtimes:
                view_runtime.remove_connection(connection, window_id=None)

        for route, view in self.running_multi_user_views.items():
            view.remove_connection(connection, window_id=None)

    def remove_view_runtime(self, view_runtime):
        user = view_runtime.start_connection.user

        self.running_single_user_views[user].remove(view_runtime)

    def get_running_views_count(self, user):
        if user not in self.running_single_user_views:
            return 0

        count = 0

        for view_runtime in self.running_single_user_views[user]:
            if not view_runtime.frontend and not view_runtime.is_stopped:
                count += 1

        return count

    def handle_lona_message(self, connection, window_id, method, url, payload):
        """
        this method gets called by the
        lona.middlewares.LonaMessageMiddleware.process_websocket_message

        """

        url_object = URL(url)

        # views
        if method == METHOD.VIEW:
            # disconnect client window from previous view
            self.remove_connection(connection, window_id)

            # resolve url
            match, route, match_info = self.server.router.resolve(
                url_object.path)

            # route is not interactive; issue a http redirect
            if match and (route.http_pass_through or not route.interactive):
                message = dumps(encode_http_redirect(window_id, url, url))
                connection.send_str(message)

                return

            # FIXME: A view runtime object has to be created always to run
            # request middlewares on the current request.
            # Otherwise authentication would not be possible.
            view_runtime = ViewRuntime(
                server=self.server,
                url=url,
                route=route,
                match_info=match_info,
                post_data=payload or {},
                start_connection=connection,
            )

            request = Request(
                view_runtime=view_runtime,
                connection=connection,
            )

            # run request middlewares
            handled, raw_response_dict, middleware = \
                self.server.run_coroutine_sync(
                    self.server.middleware_controller.process_request(
                        request=request,
                        view=view_runtime.view,
                    ),
                )

            if handled:
                # message got handled by a middleware
                if raw_response_dict:
                    view_runtime.handle_raw_response_dict(
                        raw_response_dict,
                        connections={connection: (window_id, url, )},
                    )

                return

            # reconnect or close previous started single user views
            # for this route
            user = connection.user
            running_view_runtime = None

            if user in self.running_single_user_views:
                for _view_runtime in self.running_single_user_views[user]:
                    if(_view_runtime.route == route and
                       _view_runtime.match_info == match_info and
                       _view_runtime.is_daemon):

                        running_view_runtime = _view_runtime

                        break

            if running_view_runtime:
                if not running_view_runtime.is_stopped:
                    running_view_runtime.add_connection(
                        connection=connection,
                        window_id=window_id,
                        url=url,
                    )

                    return

                else:
                    running_view_runtime.stop()

            # connect to a multi user view
            elif(route in self.running_multi_user_views):
                self.running_multi_user_views[route].add_connection(
                    connection=connection,
                    window_id=window_id,
                    url=url,
                )

                return

            # start view
            if user not in self.running_single_user_views:
                self.running_single_user_views[user] = []

            self.running_single_user_views[user].append(view_runtime)

            view_runtime.add_connection(
                connection=connection,
                window_id=window_id,
                url=url,
            )

            view_runtime.start()

        # input events
        elif method == METHOD.INPUT_EVENT:
            user = connection.user

            if user not in self.running_single_user_views:
                return

            for view_runtime in self.running_single_user_views[user]:
                if view_runtime.url == url_object:
                    view_runtime.handle_input_event(connection, payload)

                    break
