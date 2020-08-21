import asyncio
import inspect
import logging
import json
import os

from jinja2 import Environment, FileSystemLoader
from yarl import URL

from lona.protocol import InputEventType, Method, encode_html
from lona.input_event import InputEvent
from lona.html.base import AbstractNode
from lona.request import Request
from lona.utils import acquire

views_logger = logging.getLogger('lona.server.views')
templating_logger = logging.getLogger('lona.server.templating')


class UserAbort(Exception):
    pass


class SystemShutdown(Exception):
    pass


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
        self.is_class_based = False
        self.has_input_event_handler = False
        self.has_root_input_event_handler = False

        self.continue_in_background = getattr(
            self.handler, 'continue_in_background', False)

        self.multiuser = getattr(self.handler, 'multiuser', False)

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
        self.input_events = True
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

    def run(self, post_data=None):
        self.post_data = post_data
        request = Request(view=self, post_data=post_data)

        handler_args = (request,)
        handler_kwargs = dict(self.match_info or {})

        # run view
        try:
            # TODO sync vs async
            if self.is_class_based:
                raw_response_dict = self.handler.handle_request(
                    *handler_args, **handler_kwargs)

            else:
                raw_response_dict = self.handler(
                    *handler_args, **handler_kwargs)

            if raw_response_dict:
                response_dict = self.view_controller.render_response_dict(
                    raw_response_dict,
                    view_name=self.name,
                )

                if response_dict['text']:
                    # FIXME: input_events: this makes Widget.on_submit
                    # after a view is finished impossible

                    self.show_html(
                        response_dict['text'],
                        input_events=False,
                    )

                return response_dict

        except UserAbort:
            pass

        except Exception:
            # TODO: 500 handler

            raise

        finally:
            self.is_finished = True

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
    def add_connection(self, connection, window_id):
        self.connections[connection] = window_id

        self.show_html(
            html=self.html,
            input_events=self.input_events,
            connections={connection: window_id},
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
           not self.continue_in_background and
           not self.multiuser):

            self.shutdown()

    def show_html(self, html=None, input_events=True, connections={},
                  flush=False):

        # TODO: maybe a better name for "input_events"
        # TODO: maybe a better name for "flush"
        # TODO: dont send empty updates

        # if no html is set the last html gets resend
        html = html or self.html

        # collect connections to write to
        connections = connections or self.connections

        # if no connection is made, no message has to be send
        if not connections:
            # update internal state
            self.html = html
            self.input_events = input_events

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
        self.input_events = input_events

        # encode message
        # TODO: window_id
        message = json.dumps(
            encode_html(str(self.url), payload, input_events=input_events)
        )

        # send message
        for connection, window_id in connections.items():
            connection.send_str(message)

    # input events ############################################################
    def await_user_input(self, html=None, event_type='event', nodes=[]):
        async def _await_user_input():
            future = asyncio.Future()
            self.pending_user_inputs[event_type] = [future, nodes]

            return await future

        if html:
            self.show_html(html)

        return self.server.run_coroutine_sync(_await_user_input(), wait=True)

    def handle_input_event(self, event_payload):
        input_event = InputEvent(event_payload, self.html)

        # root input handler (class based views)
        if self.has_root_input_event_handler:
            input_event = self.handler.handle_root_input_event(input_event)

            if not input_event:
                self.show_html()

                return

        # widgets
        for widget in input_event.widgets:
            input_event = widget.handle_input_event(input_event)

            if not input_event:
                self.show_html()

                return

        # pending input events
        if(input_event.input_event_type != InputEventType.CUSTOM and
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
            request = Request(self, self.post_data)
            input_event = self.handler.handle_input_event(request, input_event)

            if not input_event:
                self.show_html()


class ViewController:
    def __init__(self, server):
        self.server = server

        # templating
        # TODO: warn if settings.FRONTEND_TEMPLATE is not available
        self.template_dirs = (self.server.settings.TEMPLATE_DIRS +
                              self.server.settings.CORE_TEMPLATE_DIRS)

        views_logger.debug('loading template_dirs %s',
                           repr(self.template_dirs)[1:-1])

        self.jinja2_env = Environment(
            loader=FileSystemLoader(self.template_dirs),
        )

        # cache
        views_logger.debug('setup cache')

        self.cache = {}

        if self.server.settings.VIEW_CACHE_PRELOAD:
            # TODO: implement preloading
            views_logger.debug('preloading views')

        else:
            views_logger.debug('cache is empty')

        # views
        self.running_views = {
            # user object: {
            #   route object: view object,
            # }
        }

        self.running_multi_user_views = {
            # route object: view object,
        }

    def start(self):
        # start multiuser views
        # TODO
        pass

    def shutdown(self):
        # shutdown running views per user
        for user, views in self.running_views.items():
            for route, view in views.items():
                view.shutdown(error_class=SystemShutdown)

        # TODO multi_user_views

    # templating ##############################################################
    def get_template(self, template_name):
        templating_logger.debug("searching for '%s'", template_name)

        template = self.jinja2_env.get_template(template_name)

        templating_logger.debug(
            "'%s' is '%s' ", template_name, template.filename)

        return template

    def generate_template_context(self):
        return {}  # TODO: get standard template context from settings

    def render_template(self, template_name, template_context={}):
        template = self.get_template(template_name)

        template_context = {
            **self.generate_template_context(),
            **template_context,
        }

        return template.render(template_context)

    # response dicts ##########################################################
    def render_response_dict(self, raw_response_dict, view_name):
        response_dict = {
            'status': 200,
            'content_type': 'text/html',
            'text': '',
            'file': '',
            'redirect': '',
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
                        "'%s' sets '%s' to ", view_name, key, repr(value))

        # template response
        if 'template' in raw_response_dict:
            views_logger.debug("'%s' is a template view", view_name)

            template_context = raw_response_dict

            if 'context' in template_context:
                template_context = template_context['context']

            response_dict['text'] = self.render_template(
                raw_response_dict['template'],
                template_context,
            )

        # json response
        elif 'json' in raw_response_dict:
            views_logger.debug("'%s' is a json view", view_name)

            response_dict['text'] = json.dumps(raw_response_dict['json'])

        return response_dict

    # view objects ############################################################
    def get_handler(self, import_string):
        # TODO: ambiguous log messages

        views_logger.debug("searching for '%s'", import_string)

        caching_enabled = self.server.settings.VIEW_CACHING
        ignore_import_cache = not caching_enabled
        first_load = False

        def _import_view():
            views_logger.debug("importing '%s' ignore_import_cache=%s",
                               import_string, repr(ignore_import_cache))

            path, view = acquire(
                import_string, ignore_import_cache=ignore_import_cache)

            views_logger.debug("'%s' imported from '%s'", import_string, path)

            self.cache[import_string] = {
                'path': path,
                'view': view,
                'modified': os.path.getmtime(path),
            }

        if import_string not in self.cache:
            views_logger.debug("'%s' is not cached yet", import_string)

            _import_view()
            first_load = True

        if not caching_enabled:
            path = self.cache[import_string]['path']
            modified = self.cache[import_string]['modified']

            if os.path.getmtime(path) > modified:
                views_logger.debug("'%s' is modified in file system",
                                   import_string)

                _import_view()

            elif not first_load:
                views_logger.debug("loading '%s' from cache", import_string)

        return self.cache[import_string]['view']

    def get_view(self, url, route=None, match_info=None, frontend=False):
        handler = None
        url = URL(url)

        if frontend:
            handler = (route.frontend_view or
                       self.server.settings.FRONTEND_VIEW)

        elif not route:
            match, route, match_info = self.server.router.resolve(url.path)

            if match:
                handler = route.handler

            else:  # 404: not found
                handler = self.server.settings.NOT_FOUND_404_VIEW

        else:
            handler = route.handler

        # handler is an import string
        if isinstance(handler, str):
            handler = self.get_handler(handler)

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

        # TODO: multi_user_views

    def handle_lona_message(self, connection, method, url, payload):
        """
        this method gets called by the lona_message_middleware

        """

        # TODO: if a connection starts a new view on a previously used
        # window id, the previous view should be killed

        window_id = 1  # TODO: add support for multiple windows per connection

        # views
        if method == Method.VIEW:
            # disconnect client window from previous view
            self.remove_connection(connection, window_id)

            # resolve url
            url = URL(url)
            match, route, match_info = self.server.router.resolve(url.path)

            if not match:
                # TODO: 404

                pass

            # reconnect or close previous started single user views
            # for this route
            elif(connection.user in self.running_views and
                 route in self.running_views[connection.user]):

                view = self.running_views[connection.user][route]

                if not view.is_finished and view.continue_in_background:
                    view.add_connection(
                        connection=connection, window_id=window_id)

                    return

                else:
                    view.shutdown()

            # connect to a mult user view
            elif(connection.user in self.running_multi_user_views and
                 route in self.running_multi_user_views[connection.user]):

                # TODO: implement

                pass

            # start view
            # TODO: scheduling
            view = self.get_view(
                url=url,
                route=route,
                match_info=match_info,
            )

            if connection.user not in self.running_views:
                self.running_views[connection.user] = {}

            self.running_views[connection.user][route] = view

            view.add_connection(connection, window_id)

            view.run(post_data=payload)

        # input events
        elif method == Method.INPUT_EVENT:
            if connection.user not in self.running_views:
                return

            for route, view in self.running_views[connection.user].items():
                if str(view.url) == url:
                    view.handle_input_event(payload)

                    break
