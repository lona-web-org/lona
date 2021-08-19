from concurrent.futures import CancelledError
from datetime import datetime
from enum import Enum
import threading
import logging
import asyncio
import time

from yarl import URL

from lona.exceptions import StopReason, ServerStop, UserAbort
from lona.html.abstract_node import AbstractNode
from lona.events.input_event import InputEvent
from lona.imports import get_object_repr
from lona.html.document import Document
from lona.errors import ForbiddenError
from lona.errors import ClientError
from lona._time import monotonic_ns
from lona.request import Request

from lona.protocol import (
    encode_input_event_ack,
    encode_http_redirect,
    encode_view_start,
    encode_view_stop,
    encode_redirect,
    encode_data,
    DATA_TYPE,
)


logger = logging.getLogger('lona.view_runtime')
input_events_logger = logging.getLogger('lona.input_events')


class VIEW_RUNTIME_STATE(Enum):
    NOT_STARTED = 10

    RUNNING = 21
    WAITING_FOR_IOLOOP = 22
    SLEEPING = 23
    WAITING_FOR_INPUT = 24

    FINISHED = 31
    CRASHED = 32
    STOPPED_BY_USER = 33
    STOPPED_BY_SERVER = 34


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

        # setup request
        self.request = Request(
            view_runtime=self,
            connection=self.start_connection,
        )

        # find view
        if route:
            self.view = route.view

        else:
            self.view = self.server.settings.CORE_ERROR_404_VIEW

        if frontend:
            self.view = self.server.settings.CORE_FRONTEND_VIEW

            if route and route.frontend_view:
                self.view = route.frontend_view

        self.view_class = self.server.view_loader.load(self.view)
        self.name = repr(self.view_class)

        self.view = self.view_class(
            server=self.server,
            view_runtime=self,
            request=self.request,
        )

        # setup state
        self.connections = {}
        # contains: {
        #     connection: (window_id, url),
        # }

        self.document = Document()

        self.stopped = asyncio.Future(loop=self.server.loop)
        self.is_stopped = False
        self.stop_reason = None
        self.is_daemon = False

        self.view_runtime_id = str(monotonic_ns())
        self.state = VIEW_RUNTIME_STATE.NOT_STARTED
        self.thread_ident = None
        self.thread_name = None
        self.started_at = None
        self.stopped_at = None

        self.pending_input_events = {
            'event': None,
            'click': None,
            'change': None,
        }

    # state ###################################################################
    @property
    def state(self):
        if self.is_stopped:
            if self.stop_reason is not None:
                if isinstance(self.stop_reason, UserAbort):
                    return VIEW_RUNTIME_STATE.STOPPED_BY_USER

                elif isinstance(self.stop_reason, ServerStop):
                    return VIEW_RUNTIME_STATE.STOPPED_BY_SERVER

                else:
                    return VIEW_RUNTIME_STATE.CRASHED

            else:
                return VIEW_RUNTIME_STATE.FINISHED

        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state

    # middlewares #############################################################
    def run_middlewares(self, connection, window_id, url):
        try:
            handled, raw_response_dict, middleware = \
                self.server.middleware_controller.handle_request(
                    view=self.view,
                    request=self.request,
                )

            if handled:
                if not raw_response_dict:
                    raw_response_dict = ''

                self.send_view_start(
                    connections={
                        connection: (window_id, url),
                    },
                )

                response_dict = self.handle_raw_response_dict(
                    raw_response_dict,
                )

                self.send_view_stop(
                    connections={
                        connection: (window_id, url),
                    },
                )

                return response_dict

        except ForbiddenError as exception:
            self.send_view_start(
                connections={
                    connection: (window_id, url),
                },
            )

            view_class = self.server.view_loader.load(
                self.server.settings.CORE_ERROR_403_VIEW,
            )

            view = view_class(
                server=self.server,
                view_runtime=self,
                request=self.request,
            )

            response_dict = self.handle_raw_response_dict(
                view.handle_request(
                    self.request,
                    exception=exception,
                ),
            )

            self.send_view_stop(
                connections={
                    connection: (window_id, url),
                },
            )

            return response_dict

        except Exception as exception:
            logger.error(
                'Exception raised while running middleware hooks',
                exc_info=True,
            )

            self.send_view_start(
                connections={
                    connection: (window_id, url),
                },
            )

            view_class = self.server.view_loader.load(
                self.server.settings.CORE_ERROR_500_VIEW,
            )

            view = view_class(
                server=self.server,
                view_runtime=self,
                request=self.request,
            )

            return self.handle_raw_response_dict(
                raw_response_dict=view.handle_request(
                    self.request,
                    exception=exception,
                ),
                connections={
                    connection: (window_id, url),
                },
            )

    # start and stop ##########################################################
    def run_shutdown_hook(self):
        logger.debug(
            'running %s with stop reason %s',
            self.view.on_shutdown,
            self.stop_reason,
        )

        try:
            self.view.on_shutdown(self.stop_reason)

        except Exception:
            logger.error(
                'Exception raised while running %s',
                self.view.on_shutdown,
                exc_info=True,
            )

    def start(self):
        try:
            # update internal state
            current_thread = threading.current_thread()

            self.thread_ident = current_thread.ident
            self.thread_name = current_thread.name
            self.state = VIEW_RUNTIME_STATE.RUNNING
            self.started_at = datetime.now()

            # test CLIENT_VIEW_START_TIMEOUT
            if self.server.settings.TEST_VIEW_START_TIMEOUT:
                time.sleep(self.server.settings.CLIENT_VIEW_START_TIMEOUT + 1)

            # start view
            self.send_view_start()

            # add view object to View._objects
            self.view_class._add_view_to_objects(self.view)

            # run view
            raw_response_dict = self.view.handle_request(self.request) or ''

            # response dicts
            if isinstance(raw_response_dict, AbstractNode):
                if self.route and not self.route.interactive:
                    raw_response_dict = str(raw_response_dict)

                else:
                    self.view.show(html=raw_response_dict)

                    return

            # check if non-interactive features got used in
            # interactive mode
            if(self.route and self.route.interactive and
                isinstance(raw_response_dict, dict) and (
                    'json' in raw_response_dict or
                    'file' in raw_response_dict)):

                raise RuntimeError('JSON and file responses are only available in non-interactive mode')  # NOQA

            return self.handle_raw_response_dict(raw_response_dict)

        except(StopReason, CancelledError) as _stop_reason:
            self.stop_reason = _stop_reason

        # 403 Forbidden
        except ForbiddenError as exception:
            view_class = self.server.view_loader.load(
                self.server.settings.CORE_ERROR_403_VIEW,
            )

            view = view_class(
                server=self.server,
                view_runtime=self,
                request=self.request,
            )

            return self.handle_raw_response_dict(
                view.handle_request(
                    self.request,
                    exception=exception,
                )
            )

        # 500 Internal Error
        except Exception as exception:
            self.stop_reason = exception

            logger.error(
                'Exception raised while running %s',
                self.view,
                exc_info=True,
            )

            view_class = self.server.view_loader.load(
                self.server.settings.CORE_ERROR_500_VIEW,
            )

            view = view_class(
                server=self.server,
                view_runtime=self,
                request=self.request,
            )

            return self.handle_raw_response_dict(
                view.handle_request(
                    self.request,
                    exception=exception,
                )
            )

        finally:
            self.is_stopped = True
            self.stopped_at = datetime.now()
            self.send_view_stop()

        self.run_shutdown_hook()

    def stop(self, reason=UserAbort, clean_up=True):
        self.stop_reason = reason

        if not isinstance(self.stop_reason, Exception):
            self.stop_reason = self.stop_reason()

        # let all calls on request.view.await_sync() crash with
        # the set stop reason
        def _set_stopped():
            if not self.stopped.done():
                self.stopped.set_result(True)

        self.server.loop.call_soon_threadsafe(_set_stopped)

        # cancel all pending user input events
        for pending_input_event in self.pending_input_events.copy().items():
            if not pending_input_event[1]:
                continue

            name, (future, nodes) = pending_input_event

            if not future.done():
                future.set_exception(self.stop_reason)

        # clean up
        if clean_up:
            # drop all connections
            self.connections = {}

            # multi user views have no start_connection
            if self.start_connection:
                self.server.view_runtime_controller.remove_view_runtime(self)

    def issue_500_error(self, exception):
        # stop the runtime but don't run cleanup code to get the
        # output of the 500 handle through
        self.stop(reason=exception, clean_up=False)

        # run 500 view
        self.send_view_start()

        view_class = self.server.view_loader.load(
            self.server.settings.CORE_ERROR_500_VIEW,
        )

        view = view_class(
            server=self.server,
            view_runtime=self,
            request=self.request,
        )

        self.handle_raw_response_dict(
            view.handle_request(
                self.request,
                exception=exception,
            )
        )

        self.send_view_stop()

    # connection management ###################################################
    def add_connection(self, connection, window_id, url):
        with self.document.lock:
            self.connections[connection] = (window_id, url, )

            data_type, data = self.document.serialize()

            if not data:
                return

            self.send_data(
                data=[data_type, data],
                connections={connection: (window_id, url, )},
            )

    def reconnect_connection(self, connection, window_id, url):
        with self.document.lock:
            self.connections[connection] = (window_id, url, )

            self.send_view_start(
                connections={
                    connection: (window_id, url),
                }
            )

            data_type, data = self.document.serialize()

            if not data:
                return

            self.send_data(
                data=[data_type, data],
                connections={connection: (window_id, url, )},
            )

    def remove_connection(self, connection, window_id=None):
        with self.document.lock:
            if connection in self.connections:
                if window_id:
                    if self.connections[connection][0] == window_id:
                        self.connections.pop(connection)

                else:
                    self.connections.pop(connection)

            # if the last connection gets closed and the view should
            # not continue running in background, it gets stopped
            if not self.connections and not self.is_daemon:
                self.stop()

    # lona messages ###########################################################
    def send_redirect(self, target_url, connections={}):
        with self.document.lock:
            connections = connections or self.connections

            for connection, (window_id, url) in connections.items():
                if not connection.interactive:
                    continue

                message = encode_redirect(
                    window_id=window_id,
                    view_runtime_id=self.view_runtime_id,
                    target_url=target_url,
                )

                connection.send_str(message)

    def send_http_redirect(self, target_url, connections={}):
        with self.document.lock:
            connections = connections or self.connections

            for connection, (window_id, url) in connections.items():
                if not connection.interactive:
                    continue

                message = encode_http_redirect(
                    window_id=window_id,
                    view_runtime_id=self.view_runtime_id,
                    target_url=target_url,
                )

                connection.send_str(message)

    def _send_html_update(self, title, data, connections={}):
        with self.document.lock:
            connections = connections or self.connections

            data_type, patches = data

            for connection, (window_id, url) in connections.items():
                if not connection.interactive:
                    continue

                # filter patches
                _patches = []

                for patch in patches:
                    if(patch.issuer and
                       patch.issuer == (connection, window_id)):

                        continue

                    _patches.append(patch.data)

                # send message
                message = encode_data(
                    window_id=window_id,
                    view_runtime_id=self.view_runtime_id,
                    title=title,
                    data=[data_type, _patches],
                )

                connection.send_str(message)

    def send_data(self, title=None, data=None, connections={}):
        if data and data[0] == DATA_TYPE.HTML_UPDATE:
            return self._send_html_update(
                title=title,
                data=data,
                connections=connections,
            )

        with self.document.lock:
            connections = connections or self.connections

            # send message
            for connection, (window_id, url) in connections.items():
                if not connection.interactive:
                    continue

                message = encode_data(
                    window_id=window_id,
                    view_runtime_id=self.view_runtime_id,
                    title=title,
                    data=data,
                )

                connection.send_str(message)

    def send_view_start(self, connections={}):
        with self.document.lock:
            connections = connections or self.connections

            for connection, (window_id, url) in connections.items():
                if not connection.interactive:
                    continue

                message = encode_view_start(
                    window_id=window_id,
                    view_runtime_id=self.view_runtime_id,
                )

                connection.send_str(message)

    def send_view_stop(self, connections={}):
        with self.document.lock:
            connections = connections or self.connections

            for connection, (window_id, url) in connections.items():
                if not connection.interactive:
                    continue

                message = encode_view_stop(
                    window_id=window_id,
                    view_runtime_id=self.view_runtime_id,
                )

                connection.send_str(message)

    def handle_raw_response_dict(self, raw_response_dict, connections={}):
        connections = connections or self.connections

        response_dict = self.server.response_parser.render_response_dict(
            raw_response_dict=raw_response_dict,
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
            with self.document.lock:
                data = self.document.apply(response_dict['text'])
                self.send_data(data=data, connections=connections)

        return response_dict

    # input events ############################################################
    def await_input_event(self, nodes=[], event_type='event'):
        async def _await_input_event():
            if self.pending_input_events[event_type] is not None:
                raise RuntimeError('already waiting for a {} event', str(event_type))  # NOQA

            future = asyncio.Future()
            self.pending_input_events[event_type] = [future, nodes]

            return await future

        return self.server.run_coroutine_sync(_await_input_event())

    def handle_input_event(self, connection, window_id, payload):
        input_events_logger.debug(
            'runtime #%s: handling event #%s',
            self.view_runtime_id,
            payload[0],
        )

        input_event = InputEvent(
            request=self.request,
            payload=payload,
            document=self.document,
            connection=connection,
            window_id=window_id,
        )

        def send_html_patches():
            with self.document.lock:
                data = self.document.apply(self.document.html)

                if data:
                    self.send_data(data=data)

        def log_handled_message():
            input_events_logger.debug(
                'runtime #%s: event #%s: was handled',
                self.view_runtime_id,
                payload[0],
            )

        try:
            # sending input event ack
            input_events_logger.debug(
                'runtime #%s: event #%s: sending ACK',
                self.view_runtime_id,
                payload[0],
            )

            # test CLIENT_INPUT_EVENT_TIMEOUT
            if self.server.settings.TEST_INPUT_EVENT_TIMEOUT:
                time.sleep(self.server.settings.CLIENT_INPUT_EVENT_TIMEOUT + 1)

            connection.send_str(
                encode_input_event_ack(
                    window_id=self.connections[connection][0],
                    view_runtime_id=self.view_runtime_id,
                    input_event_id=payload[0],
                )
            )

            # input event root handler
            input_events_logger.debug(
                'runtime #%s: event #%s: running View.handle_input_event_root()',  # NOQA
                self.view_runtime_id,
                payload[0],
            )

            input_event = self.view.handle_input_event_root(input_event)

            if not input_event:
                send_html_patches()

                return log_handled_message()

            # widgets
            for widget in input_event.widgets[::-1]:
                input_events_logger.debug(
                    'runtime #%s: event #%s: running %s.handle_input_event()',
                    self.view_runtime_id,
                    payload[0],
                    get_object_repr(widget),
                )

                input_event = widget.handle_input_event(input_event)

                if not input_event:
                    send_html_patches()

                    return log_handled_message()

            # pending input events
            if(input_event.name in self.pending_input_events and
               self.pending_input_events[input_event.name] is not None):

                future, nodes = self.pending_input_events[input_event.name]

                if not nodes or input_event.node in nodes:
                    input_events_logger.debug(
                        'runtime #%s: event #%s: is handled as pending %s event',  # NOQA
                        self.view_runtime_id,
                        payload[0],
                        input_event.name,
                    )

                    future.set_result(input_event)
                    self.pending_input_events[input_event.name] = None

                    return log_handled_message()

            if self.pending_input_events['event'] is not None:
                future, nodes = self.pending_input_events['event']

                if not nodes or input_event.node in nodes:
                    input_events_logger.debug(
                        'runtime #%s: event #%s: is handled as pending generic event',  # NOQA
                        self.view_runtime_id,
                        payload[0],
                    )

                    future.set_result(input_event)
                    self.pending_input_events['event'] = None

                    return log_handled_message()

            # input event handler (class based views)
            input_events_logger.debug(
                'runtime #%s: event #%s: running View.handle_input_event()',
                self.view_runtime_id,
                payload[0],
            )

            input_event = self.view.handle_input_event(input_event)

            send_html_patches()

            return log_handled_message()

        except(StopReason, CancelledError):
            input_events_logger.debug(
                'runtime #%s: event #%s: handling was stopped',
                self.view_runtime_id,
                payload[0],
            )

        except Exception as exception:
            input_events_logger.error(
                'runtime #%s: event #%s: exception occurred',
                self.view_runtime_id,
                payload[0],
                exc_info=True,
            )

            self.issue_500_error(exception)

    def handle_client_error(self, connection, window_id, payload):
        logger.error(
            'client error raised:\n%s',
            payload[0],
        )

        self.issue_500_error(ClientError(message=payload[0]))
