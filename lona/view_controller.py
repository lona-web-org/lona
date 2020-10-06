from concurrent.futures import CancelledError
import asyncio
import inspect
import logging
import json

from yarl import URL

from lona.errors import UserAbort, SystemShutdown
from lona.input_event import InputEvent
from lona.html.base import AbstractNode
from lona.utils import acquire, Mapping
from lona.request import Request

from lona.protocol import (
    encode_http_redirect,
    encode_view_start,
    encode_view_stop,
    encode_redirect,
    encode_data,
    Method,
)

views_logger = logging.getLogger('lona.server.views')


class View:
    def __init__(self, server, view_controller, url, handler, route,
                 match_info):

        self.server = server
        self.view_controller = view_controller
        self.url = url
        self.handler = handler
        self.route = route
        self.match_info = match_info

        # analyze handler
        self.is_daemon = False
        self.is_class_based = False
        self.has_input_event_handler = False
        self.has_root_input_event_handler = False

        self.multi_user = getattr(self.handler, 'multi_user', False)

        if inspect.isclass(self.handler):
            self.handler = handler()

            self.is_class_based = True

            self.has_input_event_handler = hasattr(
                self.handler, 'handle_input_event')

            self.has_root_input_event_handler = hasattr(
                self.handler, 'handle_root_input_event')

        self.name = repr(self.handler)

        # setup state
        self.connections = {}
        self.is_finished = False
        self.html = ''
        self.patch_input_events = True
        self.post_data = None

        self.pending_user_inputs = {
            'event': None,
            'click': None,
            'change': None,
            'submit': None,
            'reset': None,
        }

        # FIXME: better name
        # this is necessary to shutdown long running views
        # which are not waiting for user input
        self.shutdown_error_class = None

    def gen_request(self, connection, post_data=None):
        return Request(
            view=self,
            connection=connection,
            post_data=post_data,
            multi_user=False,
        )

    def gen_multi_user_request(self):
        return Request(
            view=self,
            connection=None,
            post_data=None,
            multi_user=True,
        )

    def run(self, request, initial_connection):
        self.post_data = request.POST
        self.initial_connection = initial_connection

        handler_args = (request,)
        handler_kwargs = dict(self.match_info or {})

        # run view
        request.connection = self.initial_connection

        try:
            self.send_view_start()

            # TODO sync vs async
            if self.is_class_based:
                raw_response_dict = self.handler.handle_request(
                    *handler_args, **handler_kwargs)

            else:
                raw_response_dict = self.handler(
                    *handler_args, **handler_kwargs)

            if raw_response_dict:
                return self.handle_raw_response_dict(raw_response_dict)

        except (CancelledError, UserAbort, SystemShutdown):
            pass

        except Exception as e:
            views_logger.error(
                'Exception raised while running %s',
                self.handler,
                exc_info=True,
            )

            return self.handle_raw_response_dict(
                self.view_controller.handle_500(request, e))

        finally:
            self.is_finished = True
            self.send_view_stop()

    def shutdown(self, error_class=UserAbort):
        self.shutdown_error_class = error_class

        # drop all connections
        self.connections = {}

        # cancel all pending user input events
        for event_name, pending in self.pending_user_inputs.items():
            if not pending:
                continue

            future, nodes = pending

            if not future.done() and not future.cancelled():
                future.set_exception(error_class())

    # connection managment ####################################################
    def add_connection(self, connection, window_id, url):
        self.connections[connection] = (window_id, url, )

        self.send_data(
            html=self.html,
            patch_input_events=self.patch_input_events,
            connections={connection: (window_id, url, )},
            flush=True,
        )

    def remove_connection(self, connection, window_id=None):
        if connection in self.connections:
            if window_id:
                if self.connections[connection] == window_id:
                    self.connections.pop(connection)

            else:
                self.connections.pop(connection)

        # if the last connection gets closed and the user should
        # not continue running in background, it gets shutdown
        if(not self.connections and
           not self.is_daemon and
           not self.multi_user):

            self.shutdown()

    # lona messages ###########################################################
    def send_redirect(self, target_url, connections={}):
        connections = connections or self.connections

        for connection, window_id in connections.items():
            message = json.dumps(
                encode_redirect(window_id, str(self.url), target_url))

            connection.send_str(message)

    def send_http_redirect(self, target_url, connections={}):
        connections = connections or self.connections

        for connection, window_id in connections.items():
            message = json.dumps(
                encode_http_redirect(window_id, str(self.url), target_url))

            connection.send_str(message)

    def send_data(self, title=None, html=None, widget_data=None,
                  connections={}, flush=False, patch_input_events=True):

        connections = connections or self.connections

        # this mode gets used by request.client.set_title()
        if title and not html and not widget_data:
            payload = None

        else:
            # if no html is set the last html gets resend
            html = html or self.html

            # if no connection is made, no message has to be send
            if not connections:
                # update internal state
                self.html = html
                self.patch_input_events = patch_input_events

                return

            # node trees
            if isinstance(html, AbstractNode):
                if not flush and html is self.html:
                    payload = html.get_dirty_nodes()
                    html.clean()

                else:
                    payload = html.serialize()

            # html strings
            else:
                payload = str(html)

            # update internal state
            self.html = html
            self.patch_input_events = patch_input_events

        # send message
        for connection, (window_id, url) in list(connections.items()):
            message = json.dumps(
                encode_data(
                    window_id=window_id,
                    url=url,
                    title=title,
                    html=payload,
                    widget_data=None,
                    patch_input_events=patch_input_events,
                )
            )

            connection.send_str(message)

    def send_view_start(self, connections={}):
        connections = connections or self.connections

        for connection, (window_id, url) in list(connections.items()):
            message = json.dumps(
                encode_view_start(window_id=window_id, url=url))

            connection.send_str(message)

    def send_view_stop(self, connections={}):
        connections = connections or self.connections

        for connection, (window_id, url) in list(connections.items()):
            message = json.dumps(
                encode_view_stop(window_id=window_id, url=url))

            connection.send_str(message)

    def handle_raw_response_dict(self, raw_response_dict,
                                 patch_input_events=None, connections={}):

        connections = connections or self.connections

        if patch_input_events is None:
            patch_input_events = self.patch_input_events

        response_dict = self.view_controller.render_response_dict(
            raw_response_dict,
            view_name=self.name,
        )

        if response_dict['redirect']:
            self.send_redirect(
                response_dict['redirect'],
                connections=connections,
            )

        elif response_dict['http_redirect']:
            self.send_http_redirect(
                response_dict['http_redirect'],
                connections=connections,
            )

        elif response_dict['text']:
            self.send_data(
                html=response_dict['text'],
                patch_input_events=self.patch_input_events,
                connections=connections,
            )

        return response_dict

    # input events ############################################################
    def await_user_input(self, html=None, event_type='event', nodes=[]):
        # TODO: find right priority

        async def _await_user_input():
            future = asyncio.Future()
            self.pending_user_inputs[event_type] = [future, nodes]

            return await future

        if html:
            self.send_data(html=html)

        return self.server.schedule(
            _await_user_input(),
            sync=True,
            wait=True,
            priority=self.server.settings.DEFAULT_VIEW_PRIORITY,
        )

    def handle_input_event(self, event_payload):
        input_event = InputEvent(event_payload, self.html)

        # root input handler (class based views)
        if self.has_root_input_event_handler:
            input_event = self.handler.handle_root_input_event(input_event)

            if not input_event:
                self.send_data()

                return

        # widgets
        for widget in input_event.widgets:
            input_event = widget.handle_input_event(input_event)

            if not input_event:
                self.send_data()

                return

        # pending input events
        if(input_event.name in self.pending_user_inputs and
           self.pending_user_inputs[input_event.name] is not None):

            future, nodes = self.pending_user_inputs[input_event.name]

            if not nodes or input_event.node in nodes:
                future.set_result(input_event)
                self.pending_user_inputs[input_event.name] = None

                return

        if self.pending_user_inputs['event'] is not None:
            future, nodes = self.pending_user_inputs['event']

            if not nodes or input_event.node in nodes:
                future.set_result(input_event)
                self.pending_user_inputs['event'] = None

                return

        # root input handler (class based views)
        if self.has_input_event_handler:
            request = Request(
                view=self,
                connection=self.initial_connection,
                post_data=self.post_data,
            )

            input_event = self.handler.handle_input_event(request, input_event)

            if not input_event:
                self.send_data()


class ViewController:
    def __init__(self, server):
        self.server = server

        # cache
        views_logger.debug('setup cache')

        self.cache = {}

        if self.server.settings.VIEW_CACHE_PRELOAD:
            # TODO: implement preloading
            views_logger.debug('preloading views')

        else:
            views_logger.debug('cache is empty')

        # views
        self.running_views = Mapping()
        # prototype: {
        #    user object: {
        #      route object: view object,
        #    }
        # }

        self.running_multi_user_views = Mapping()
        # prototype: {
        #    route object: view object,
        # }

    def start(self):
        # TODO: add support for custom view priorities

        # error handler
        views_logger.debug('loading error handler')

        views_logger.debug(
            "loading 404 handler from '%s'",
            self.server.settings.ERROR_404_HANDLER,
        )

        self.error_404_handler = acquire(
            self.server.settings.ERROR_404_HANDLER)[1]

        views_logger.debug(
            "loading 404 fallback handler from '%s'",
            self.server.settings.ERROR_404_FALLBACK_HANDLER,
        )

        self.error_404_fallback_handler = acquire(
            self.server.settings.ERROR_404_FALLBACK_HANDLER)[1]

        views_logger.debug(
            "loading 500 handler from '%s'",
            self.server.settings.ERROR_500_HANDLER,
        )

        self.error_500_handler = acquire(
            self.server.settings.ERROR_500_HANDLER)[1]

        views_logger.debug(
            "loading 500 fallback handler from '%s'",
            self.server.settings.ERROR_500_FALLBACK_HANDLER,
        )

        self.error_500_fallback_handler = acquire(
            self.server.settings.ERROR_500_FALLBACK_HANDLER)[1]

        # multi user views
        views_logger.debug('starting multi user views')

        for route in self.server.router.routes:
            view = self.get_view(route=route)

            if view.multi_user:
                views_logger.debug('starting %s as multi user view', view)

                request = view.gen_multi_user_request()
                self.running_multi_user_views[route] = view

                priority = \
                    self.server.settings.DEFAULT_MULTI_USER_VIEW_PRIORITY

                self.server.schedule(
                    view.run,
                    request=request,
                    initial_connection=None,
                    priority=priority,
                )

    def shutdown(self):
        # shutdown running views per user
        for user, views in self.running_views.items():
            for route, view in views.items():
                view.shutdown(error_class=SystemShutdown)

        # shutdown multi user views
        for route, view in self.running_multi_user_views.items():
            view.shutdown(error_class=SystemShutdown)

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

        # string response
        if isinstance(raw_response_dict, str):
            views_logger.debug("'%s' is a string based view", view_name)

            response_dict['text'] = raw_response_dict

        # find keys
        elif isinstance(raw_response_dict, dict):
            for key in response_dict.keys():
                if key in raw_response_dict:
                    value = raw_response_dict[key]
                    response_dict[key] = value

                    views_logger.debug(
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
            views_logger.debug("'%s' is a template view", view_name)

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
            views_logger.debug("'%s' is a json view", view_name)

            response_dict['text'] = json.dumps(raw_response_dict['json'])

        return response_dict

    # error handler ###########################################################
    def handle_404(self, request):
        try:
            return self.error_404_handler(request)

        except Exception:
            views_logger.error(
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
            views_logger.error(
                'Exception occurred while running %s. Falling back to %s',
                self.error_500_handler,
                self.error_500_fallback_handler,
                exc_info=True,
            )

        return self.error_500_fallback_handler(request, exception)

    # view objects ############################################################
    def get_view(self, url=None, route=None, match_info=None, frontend=False):
        handler = None

        if not url and not route:
            raise ValueError

        if url:
            url = URL(url)

        if frontend:
            handler = self.server.settings.FRONTEND_VIEW

            if route and route.frontend_view:
                handler = route.frontend_view

        elif url:
            match, route, match_info = self.server.router.resolve(url.path)

            if match:
                handler = route.handler

            else:
                handler = self.handle_404

        else:
            handler = route.handler

        # handler is an import string
        if isinstance(handler, str):
            handler = self.server.view_loader.load(handler)

        return View(
            server=self.server,
            view_controller=self,
            url=url,
            handler=handler,
            route=route,
            match_info=match_info,
        )

    # view managment ##########################################################
    def remove_connection(self, connection, window_id=None):
        for user, views in self.running_views.items():
            for route, view in views.items():
                view.remove_connection(connection, window_id=None)

        for route, view in self.running_multi_user_views.items():
            view.remove_connection(connection, window_id=None)

    def run_middlewares(self, request, view):
        for middleware in self.server.request_middlewares:
            views_logger.debug('running %s on %s', middleware, request)

            raw_response_dict = self.server.schedule(
                middleware,
                self.server,
                request,
                view.handler,
                priority=self.server.settings.REQUEST_MIDDLEWARE_PRIORITY,
                sync=True,
                wait=True,
            )

            if raw_response_dict:
                views_logger.debug('request got handled by %s', middleware)

                return raw_response_dict

    def run_view_non_interactive(self, url, connection, route=None,
                                 match_info=None, frontend=False,
                                 post_data=None):

        view = self.get_view(
            url=url,
            route=route,
            match_info=match_info,
            frontend=frontend,
        )

        request = view.gen_request(
            connection=connection,
            post_data=post_data,
        )

        raw_response_dict = self.run_middlewares(request, view)

        if raw_response_dict:
            # request got handled by a middleware

            return view.handle_raw_response_dict(raw_response_dict)

        return view.run(
            request=request,
            initial_connection=connection,
        )

    def handle_lona_message(self, connection, window_id, method, url, payload):
        """
        this method gets called by the
        lona.middlewares.websocket_middlewares.lona_message_middleware

        """

        url_object = URL(url)

        # views
        if method == Method.VIEW:
            # disconnect client window from previous view
            self.remove_connection(connection, window_id)

            # resolve url
            match, route, match_info = self.server.router.resolve(
                url_object.path)

            # route is not interactive; issue a http redirect
            if match and route.http_pass_through or not route.interactive:
                message = json.dumps(encode_http_redirect(window_id, url, url))
                connection.send_str(message)

                return

            # A View object has to be retrieved always to run
            # REQUEST_MIDDLEWARES on the current request.
            # Otherwise authentication would not be possible.
            view = self.get_view(
                url=url,
                route=route,
                match_info=match_info,
            )

            request = view.gen_request(
                connection=connection,
                post_data=payload,
            )

            # run request middlewares
            raw_response_dict = self.run_middlewares(request, view)

            if raw_response_dict:
                # message got handled by a middleware

                view.handle_raw_response_dict(
                    raw_response_dict,
                    connections={connection: (window_id, url, )},
                    patch_input_events=False,
                )

                return

            # reconnect or close previous started single user views
            # for this route
            if(connection.user in self.running_views and
               route in self.running_views[connection.user] and
               self.running_views[connection.user][route].is_daemon):

                view = self.running_views[connection.user][route]

                if not view.is_finished and view.is_daemon:
                    view.add_connection(
                        connection=connection,
                        window_id=window_id,
                        url=url,
                    )

                    return

                else:
                    view.shutdown()

            # connect to a multi user view
            elif(route in self.running_multi_user_views):
                self.running_multi_user_views[route].add_connection(
                    connection=connection,
                    window_id=window_id,
                    url=url,
                )

                return

            # start view
            if connection.user not in self.running_views:
                self.running_views[connection.user] = {}

            self.running_views[connection.user][route] = view

            view.add_connection(
                connection=connection,
                window_id=window_id,
                url=url,
            )

            view.run(request=request, initial_connection=connection)

        # input events
        elif method == Method.INPUT_EVENT:
            if connection.user not in self.running_views:
                return

            for route, view in self.running_views[connection.user].items():
                if view.url == url_object:
                    view.handle_input_event(payload)

                    break
