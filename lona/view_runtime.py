from concurrent.futures import CancelledError
import logging
import asyncio
import json

from yarl import URL

from lona.exceptions import StopReason, UserAbort
from lona.input_event import InputEvent
from lona.html.base import AbstractNode
from lona.request import Request

from lona.protocol import (
    encode_http_redirect,
    encode_view_start,
    encode_view_stop,
    encode_redirect,
    encode_data,
)

logger = logging.getLogger('lona.view_runtime')


class ViewRuntime:
    def __init__(self, server, url, route, match_info, post_data={},
                 frontend=False, start_connection=None):

        self.server = server
        self.url = URL(url or '')
        self.route = route
        self.match_info = match_info
        self.post_data = post_data
        self.frontend = frontend
        self.start_connection = start_connection

        # find view
        if route:
            self.view = route.view

        else:
            self.view = self.server.settings.ERROR_404_HANDLER

        if frontend:
            self.view = self.server.settings.FRONTEND_VIEW

            if route and route.frontend_view:
                self.view = route.frontend_view

        self.view = self.server.view_loader.load(self.view)
        self.view_spec = self.server.view_loader.get_view_spec(self.view)
        self.name = repr(self.view)

        if self.view_spec.is_class_based:
            self.view = self.view()

        # setup state
        self.connections = {}
        # contains: {
        #     connection: (window_id, url),
        # }

        self.is_finished = False
        self.stop_reason = None
        self.is_daemon = False

        self.html = ''
        self.patch_input_events = True

        self.pending_input_events = {
            'event': None,
            'click': None,
            'change': None,
            'submit': None,
            'reset': None,
        }

    def start(self):
        request = Request(
            view_runtime=self,
            connection=self.start_connection,
        )

        view_args = (request,)
        view_kwargs = dict(self.match_info or {})

        # start view
        try:
            self.send_view_start()

            if self.view_spec.is_class_based:
                raw_response_dict = self.view.handle_request(
                    *view_args, **view_kwargs)

            else:
                raw_response_dict = self.view(*view_args, **view_kwargs)

            if raw_response_dict:
                return self.handle_raw_response_dict(raw_response_dict)

        except(StopReason, CancelledError):
            pass

        except Exception as e:
            logger.error(
                'Exception raised while running %s',
                self.view,
                exc_info=True,
            )

            return self.handle_raw_response_dict(
                self.server.view_runtime_controller.handle_500(request, e))

        finally:
            self.is_finished = True
            self.send_view_stop()

    def stop(self, reason=UserAbort):
        self.stop_reason = reason

        # drop all connections
        self.connections = {}

        # cancel all pending user input events
        for event_name, pending in self.pending_input_events.items():
            if not pending:
                continue

            future, nodes = pending

            if not future.done() and not future.cancelled():
                future.set_exception(self.stop_reason())

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
        # not continue running in background, it gets stopped
        if(not self.connections and
           not self.is_daemon and
           not self.view_spec.multi_user):

            self.stop()

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

        response_dict = \
            self.server.view_runtime_controller.render_response_dict(
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
    def await_input_event(self, html=None, event_type='event', nodes=[]):
        # TODO: find right priority

        async def _await_input_event():
            future = asyncio.Future()
            self.pending_input_events[event_type] = [future, nodes]

            return await future

        if html:
            self.send_data(html=html)

        return self.server.schedule(
            _await_input_event(),
            sync=True,
            wait=True,
            priority=self.server.settings.DEFAULT_VIEW_PRIORITY,
        )

    def handle_input_event(self, connection, event_payload):
        input_event = InputEvent(event_payload, self.html)

        # root input handler (class based views)
        if self.view_spec.has_root_input_event_handler:
            input_event = self.view.handle_root_input_event(input_event)

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
        if(input_event.name in self.pending_input_events and
           self.pending_input_events[input_event.name] is not None):

            future, nodes = self.pending_input_events[input_event.name]

            if not nodes or input_event.node in nodes:
                future.set_result(input_event)
                self.pending_input_events[input_event.name] = None

                return

        if self.pending_input_events['event'] is not None:
            future, nodes = self.pending_input_events['event']

            if not nodes or input_event.node in nodes:
                future.set_result(input_event)
                self.pending_input_events['event'] = None

                return

        # root input handler (class based views)
        if self.view_spec.has_input_event_handler:
            request = Request(
                view_runtime=self,
                connection=connection,
            )

            input_event = self.view.handle_input_event(request, input_event)

            if not input_event:
                self.send_data()
