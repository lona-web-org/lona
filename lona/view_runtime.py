from __future__ import annotations

from typing import TYPE_CHECKING, Dict, cast, Any
from collections.abc import Container, Awaitable
from concurrent.futures import CancelledError
from datetime import datetime
from enum import Enum
import threading
import logging
import asyncio
import time

from typing_extensions import Literal
from yarl import URL

from lona.protocol import (
    encode_input_event_ack,
    encode_http_redirect,
    encode_view_start,
    encode_view_stop,
    encode_redirect,
    encode_data,
    DATA_TYPE,
)
from lona.errors import ForbiddenError, NotFoundError, ClientError
from lona.exceptions import StopReason, ServerStop, UserAbort
from lona.html.abstract_node import AbstractNode
from lona.unique_ids import generate_unique_id
from lona.events.input_event import InputEvent
from lona.imports import get_object_repr
from lona.html.document import Document
from lona.request import Request

# avoid import cycles
if TYPE_CHECKING:  # pragma: no cover
    from lona.server import LonaServer


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
    def __init__(self, server, url, route, match_info, post_data=None,
                 frontend=False, start_connection=None):

        self.server: LonaServer = server
        self.url = URL(url or '')
        self.route = route
        self.match_info = match_info
        self.post_data = post_data or {}
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

        self.view_class = self.server._view_loader.load(self.view)
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

        self.stopped: asyncio.Future[Literal[True]] = asyncio.Future(loop=self.server.loop)  # NOQA: LN001
        self.is_stopped = False
        self.stop_reason = None
        self.is_daemon = False

        self.view_runtime_id = generate_unique_id(name_space='view_runtimes')
        self.state = VIEW_RUNTIME_STATE.NOT_STARTED
        self.thread_ident = None
        self.thread_name = None
        self.started_at = None
        self.stopped_at = None

        self.pending_input_events = {
            'event': None,
            'click': None,
            'change': None,
            'focus': None,
            'blur': None,
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

    # error views #############################################################
    def run_error_view(
            self,
            view_name: str,
            exception: Exception,
            send_view_start: bool = False,
            send_view_stop: bool = False,
            connections: dict | None = None,
    ) -> Dict[str, Any]:

        if send_view_start:
            self.send_view_start(connections=connections)

        view_class = self.server._view_loader.load(view_name)

        view = view_class(
            server=self.server,
            view_runtime=self,
            request=self.request,
        )

        view_kwargs = {
            'request': self.request,
        }

        # 404 Not Found error views have no argument 'exception'
        if view_name != self.server.settings.CORE_ERROR_404_VIEW:
            view_kwargs['exception'] = exception

        response_dict = self.handle_raw_response_dict(
            view.handle_request(**view_kwargs),
        )

        if send_view_stop:
            self.send_view_stop(connections)

        return cast(Dict[str, Any], response_dict)

    # middlewares #############################################################
    def run_middlewares(self, connection, window_id, url):
        try:
            handled, raw_response_dict, middleware = \
                self.server._middleware_controller.handle_request(
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

        # 403 Forbidden
        except ForbiddenError as exception:
            return self.run_error_view(
                view_name=self.server.settings.CORE_ERROR_403_VIEW,
                exception=exception,
                send_view_start=True,
                send_view_stop=True,
                connections={
                    connection: (window_id, url),
                },
            )

        # 404 Not Found
        except NotFoundError as exception:
            self.stop_reason = exception

            return self.run_error_view(
                view_name=self.server.settings.CORE_ERROR_404_VIEW,
                exception=exception,
                send_view_start=True,
                send_view_stop=True,
                connections={
                    connection: (window_id, url),
                },
            )

        # 500 Internal Error
        except Exception as exception:
            logger.exception('Exception raised while running middleware hooks')

            return self.run_error_view(
                view_name=self.server.settings.CORE_ERROR_500_VIEW,
                exception=exception,
                send_view_start=True,
                send_view_stop=True,
                connections={
                    connection: (window_id, url),
                },
            )

    # start and stop ##########################################################
    def run_stop_hook(self):
        logger.debug(
            'running %s with stop reason %s',
            self.view.on_stop,
            self.stop_reason,
        )

        try:
            self.view.on_stop(self.stop_reason)

        except Exception:
            logger.exception(
                'Exception raised while running %s',
                self.view.on_stop,
            )

    def run_cleanup_hook(self):
        from lona.view import LonaView

        # FIXME: this inline import is necessary to avoid circular import
        # this can be fixed by moving runtime state changes from LonaView to
        # ViewRuntime

        def _run():
            logger.debug('running %s', self.view.on_cleanup)

            try:
                self.view.on_cleanup()

            except Exception:
                logger.exception(
                    'Exception raised while running %s',
                    self.view.on_cleanup,
                )

        # if on_cleanup is not defined by the view class
        # it is unnecessary to start a thread
        if self.view_class.on_cleanup is LonaView.on_cleanup:
            return

        self.server.run_function_async(_run)

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
            if (self.route and self.route.interactive and
                    isinstance(raw_response_dict, dict) and (
                        'json' in raw_response_dict or
                        'file' in raw_response_dict or
                        'headers' in raw_response_dict or
                        'body' in raw_response_dict)):

                raise RuntimeError(
                    'JSON, binary and file responses and headers are only available in non-interactive mode',
                )

            return self.handle_raw_response_dict(raw_response_dict)

        # view got stopped from outside
        except (StopReason, CancelledError) as exception:
            self.stop_reason = exception

        # 403 Forbidden
        except ForbiddenError as exception:
            self.stop_reason = exception

            return self.run_error_view(
                view_name=self.server.settings.CORE_ERROR_403_VIEW,
                exception=exception,
                send_view_start=False,
                send_view_stop=False,
            )

        # 404 Not Found
        except NotFoundError as exception:
            self.stop_reason = exception

            return self.run_error_view(
                view_name=self.server.settings.CORE_ERROR_404_VIEW,
                exception=exception,
                send_view_start=False,
                send_view_stop=False,
            )

        # 500 Internal Error
        except Exception as exception:
            self.stop_reason = exception

            logger.exception('Exception raised while running %s', self.view)

            return self.run_error_view(
                view_name=self.server.settings.CORE_ERROR_500_VIEW,
                exception=exception,
                send_view_start=False,
                send_view_stop=False,
            )

        finally:
            self.is_stopped = True
            self.stopped_at = datetime.now()
            self.send_view_stop()
            self.run_stop_hook()

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
                self.server._view_runtime_controller.remove_view_runtime(self)

    def issue_500_error(self, exception):
        # stop the runtime but don't run cleanup code to get the
        # output of the 500 handle through
        self.stop(reason=exception, clean_up=False)

        self.run_error_view(
            view_name=self.server.settings.CORE_ERROR_500_VIEW,
            exception=exception,
            send_view_start=True,
            send_view_stop=True,
        )

    # connection management ###################################################
    def add_connection(
            self,
            connection,
            window_id,
            url,
            send_view_start=False,
    ):

        with self.document.lock:
            self.connections[connection] = (window_id, url)

            if send_view_start:
                self.send_view_start(
                    connections={
                        connection: (window_id, url),
                    },
                )

            title, data_type, data = self.document.serialize()

            if not data_type or not data:
                return

            self.send_data(
                title=title,
                data=[data_type, data],
                connections={connection: (window_id, url)},
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
    def send_redirect(self, target_url, connections=None):
        with self.document.lock:
            connections = connections or self.connections

            for connection, (window_id, _url) in connections.items():
                if not connection.interactive:
                    continue

                message = encode_redirect(
                    window_id=window_id,
                    view_runtime_id=self.view_runtime_id,
                    target_url=target_url,
                )

                connection.send_str(message)

    def send_http_redirect(self, target_url, connections=None):
        with self.document.lock:
            connections = connections or self.connections

            for connection, (window_id, _url) in connections.items():
                if not connection.interactive:
                    continue

                message = encode_http_redirect(
                    window_id=window_id,
                    view_runtime_id=self.view_runtime_id,
                    target_url=target_url,
                )

                connection.send_str(message)

    def _send_html_update(self, title, data, connections=None):
        with self.document.lock:
            connections = connections or self.connections

            data_type, patches = data

            for connection, (window_id, _url) in connections.items():
                if not connection.interactive:
                    continue

                # filter patches
                _patches = []

                for patch in patches:
                    if (patch.issuer and
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

    def send_data(self, title=None, data=None, connections=None):
        if data and data[0] == DATA_TYPE.HTML_UPDATE:
            return self._send_html_update(
                title=title,
                data=data,
                connections=connections or {},
            )

        with self.document.lock:
            connections = connections or self.connections

            # send message
            for connection, (window_id, _url) in connections.items():
                if not connection.interactive:
                    continue

                message = encode_data(
                    window_id=window_id,
                    view_runtime_id=self.view_runtime_id,
                    title=title,
                    data=data,
                )

                connection.send_str(message)

    def send_view_start(self, connections=None):
        with self.document.lock:
            connections = connections or self.connections

            for connection, (window_id, _url) in connections.items():
                if not connection.interactive:
                    continue

                message = encode_view_start(
                    window_id=window_id,
                    view_runtime_id=self.view_runtime_id,
                )

                connection.send_str(message)

    def send_view_stop(self, connections=None):
        with self.document.lock:
            connections = connections or self.connections

            for connection, (window_id, _url) in connections.items():
                if not connection.interactive:
                    continue

                message = encode_view_stop(
                    window_id=window_id,
                    view_runtime_id=self.view_runtime_id,
                )

                connection.send_str(message)

    def handle_raw_response_dict(self, raw_response_dict, connections=None):
        connections = connections or self.connections

        response_dict = self.server._response_parser.render_response_dict(
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
                title, data_type, data = self.document.apply(
                    html=response_dict['text'],
                )

                self.send_data(
                    title=title,
                    data=[data_type, data],
                    connections=connections,
                )

        return response_dict

    # input events ############################################################
    def await_input_event(
            self,
            nodes: None | Container[AbstractNode] = None,
            event_type: str = 'event',
    ) -> InputEvent:
        async def _await_input_event() -> InputEvent:
            if self.pending_input_events[event_type] is not None:
                raise RuntimeError(f'already waiting for a {event_type} event')

            future: Awaitable[InputEvent] = asyncio.Future()
            self.pending_input_events[event_type] = [future, nodes or []]

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
                title, data_type, data = self.document.apply(
                    html=self.document.html,
                )

                if data_type and data:
                    self.send_data(
                        title=title,
                        data=[data_type, data],
                    )

        def log_handled_message():
            input_events_logger.debug(
                'runtime #%s: event #%s: was handled',
                self.view_runtime_id,
                payload[0],
            )

        def run_handler(handler, input_event):
            return_value = handler(input_event)

            if not isinstance(return_value, (InputEvent, dict, type(None))):
                raise RuntimeError(
                    '%r returned an unexpected type (%r)',
                    handler,
                    return_value,
                )

            if isinstance(return_value, dict):
                response_parser = self.server._response_parser

                response_dict = response_parser.parse_event_response_dict(
                    return_value,
                )

                self.handle_raw_response_dict(response_dict)

                return response_dict

            return return_value

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
                ),
            )

            # input event root handler
            input_events_logger.debug(
                'runtime #%s: event #%s: running View.handle_input_event_root()',
                self.view_runtime_id,
                payload[0],
            )

            return_value = run_handler(
                self.view.handle_input_event_root,
                input_event,
            )

            if isinstance(return_value, dict):
                return log_handled_message()

            elif not return_value:
                send_html_patches()

                return log_handled_message()

            else:
                input_event = return_value

            # node input event handler
            for node in input_event.nodes:
                input_events_logger.debug(
                    'runtime #%s: event #%s: running %s.handle_input_event()',
                    self.view_runtime_id,
                    payload[0],
                    get_object_repr(node),
                )

                return_value = run_handler(
                    node.handle_input_event,
                    input_event,
                )

                if isinstance(return_value, dict):
                    return log_handled_message()

                elif not return_value:
                    send_html_patches()

                    return log_handled_message()

                else:
                    input_event = return_value

            # pending input events
            if (input_event.name in self.pending_input_events and
                    self.pending_input_events[input_event.name] is not None):

                future, nodes = self.pending_input_events[input_event.name]

                if not nodes or input_event.node in nodes:
                    input_events_logger.debug(
                        'runtime #%s: event #%s: is handled as pending %s event',
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
                        'runtime #%s: event #%s: is handled as pending generic event',
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

            return_value = run_handler(
                self.view.handle_input_event,
                input_event,
            )

            if isinstance(return_value, dict):
                return log_handled_message()

            send_html_patches()

            return log_handled_message()

        except (StopReason, CancelledError):
            input_events_logger.debug(
                'runtime #%s: event #%s: handling was stopped',
                self.view_runtime_id,
                payload[0],
            )

        except Exception as exception:
            input_events_logger.exception(
                'runtime #%s: event #%s: exception occurred',
                self.view_runtime_id,
                payload[0],
            )

            self.issue_500_error(exception)

    def handle_client_error(self, connection, window_id, payload):
        logger.error(
            'client error raised:\n%s',
            payload[0],
        )

        self.issue_500_error(ClientError(message=payload[0]))
