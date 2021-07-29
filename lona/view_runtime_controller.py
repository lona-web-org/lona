import logging

from yarl import URL

from lona.protocol import encode_http_redirect, METHOD
from lona.view_runtime import ViewRuntime
from lona.exceptions import ServerStop

input_events_logger = logging.getLogger('lona.input_events')
views_logger = logging.getLogger('lona.views')


class ViewRuntimeController:
    def __init__(self, server):
        self.server = server

        self._view_runtimes = {
            # contains: view_runtime_id: view_runtime
        }

    def start(self):
        pass

    def stop(self):
        for view_runtime in self.iter_view_runtimes():
            view_runtime.stop(reason=ServerStop)

    # helper ##################################################################
    def get_view_runtime(self, view_runtime_id):
        try:
            return self._view_runtimes[view_runtime_id]

        except KeyError:
            return None

    def get_running_view_runtime(self, user, route, match_info):
        for view_runtime in self.iter_view_runtimes():
            if(view_runtime.start_connection.user == user and
               view_runtime.is_daemon and
               view_runtime.route == route and
               view_runtime.match_info == match_info):

                return view_runtime

    def remove_view_runtime(self, view_runtime):
        try:
            self._view_runtimes.pop(view_runtime.view_runtime_id)

        except KeyError:
            pass

        view_runtime.view_class._remove_view_from_objects(view_runtime.view)

    def iter_view_runtimes(self):
        view_runtime_ids = list(self._view_runtimes.keys())

        for view_runtime_id in view_runtime_ids:
            view_runtime = self.get_view_runtime(view_runtime_id)

            if not view_runtime:
                continue

            yield view_runtime

    def remove_connection(self, connection, window_id=None):
        for view_runtime in self.iter_view_runtimes():
            view_runtime.remove_connection(
                connection=connection,
                window_id=window_id,
            )

    def get_running_views_count(self, user):
        count = 0

        for view_runtime in self.iter_view_runtimes():
            if(view_runtime.start_connection and
               view_runtime.start_connection.user == user):

                count += 1

        return count

    # lona messages ###########################################################
    def handle_input_event_message(self, connection, window_id,
                                   view_runtime_id, method, payload):

        view_runtime = self.get_view_runtime(view_runtime_id)

        if not view_runtime:
            input_events_logger.debug(
                'event #%s: runtime id is unknown. event is skipped',
                payload[0],
            )

            return

        if connection.user != view_runtime.start_connection.user:
            input_events_logger.debug(
                'event #%s: connection.user is not authorized. event is skipped',  # NOQA
                payload[0],
            )

            return

        input_events_logger.debug(
            'event #%s: gets handled by runtime #%s',
            payload[0],
            view_runtime_id,
        )

        view_runtime.handle_input_event(
            connection=connection,
            window_id=window_id,
            payload=payload,
        )

    def handle_client_error_message(self, connection, window_id,
                                    view_runtime_id, method, payload):

        view_runtime = self.get_view_runtime(view_runtime_id)

        if not view_runtime:
            views_logger.debug(
                'runtime id is unknown. event is skipped',
                payload[0],
            )

            return

        if connection.user != view_runtime.start_connection.user:
            views_logger.debug(
                'connection.user is not authorized. client error is skipped',  # NOQA
            )

            return

        views_logger.debug(
            'client error gets handled by runtime #%s',
            view_runtime_id,
        )

        view_runtime.handle_client_error(
            connection=connection,
            window_id=window_id,
            payload=payload,
        )

    def handle_view_message(self, connection, window_id, view_runtime_id,
                            method, payload):

        url, post_data = payload

        # resolve url
        url_object = URL(url)
        match, route, match_info = self.server.router.resolve(url_object.path)

        # route is not interactive; issue a http redirect
        if(connection.interactive and
           match and
           (route.http_pass_through or not route.interactive)):

            views_logger.debug('route is not interactive; issue a http redirect')  # NOQA

            message = encode_http_redirect(
                window_id=window_id,
                view_runtime_id=None,
                target_url=url,
            )

            connection.send_str(message)

            views_logger.debug('message handled')

            return

        # reconnect to daemonized view runtime ################################
        if connection.interactive:
            views_logger.debug('removing old connections')

            self.remove_connection(
                connection,
                window_id=window_id,
            )

            # search for a runnnig view runtime to reconnect to
            views_logger.debug('searching for running view runtime')

            running_view_runtime = self.get_running_view_runtime(
                user=connection.user,
                route=route,
                match_info=match_info,
            )

            if running_view_runtime and not running_view_runtime.is_stopped:
                views_logger.debug(
                    'reconnecting to %s',
                    repr(running_view_runtime),
                )

                running_view_runtime.reconnect_connection(
                    connection=connection,
                    window_id=window_id,
                    url=url,
                )

                views_logger.debug('message handled')

                return

        # start new view runtime ##############################################
        # remove previous running runtime
        if connection.interactive and running_view_runtime:
            views_logger.debug('removing previous runtime')

            self.server.view_runtime_controller.remove_view_runtime(
                view_runtime=running_view_runtime
            )

        # start nev runtime
        views_logger.debug('trying to start a new view runtime')

        frontend = False

        if not connection.interactive and match and route.interactive:
            frontend = True

            views_logger.debug('running in frontend mode')

        view_runtime = ViewRuntime(
            server=self.server,
            url=url,
            route=route,
            match_info=match_info,
            post_data=post_data or {},
            start_connection=connection,
            frontend=frontend,
        )

        if connection.interactive:
            view_runtime.add_connection(
                connection=connection,
                window_id=window_id,
                url=url,
            )

        # run middlewares
        response_dict = view_runtime.run_middlewares(
            connection=connection,
            window_id=window_id,
            url=url,
        )

        # request got handled by a middleware
        if response_dict:
            views_logger.debug('connection was refused by middleware')

            return response_dict

        self._view_runtimes[view_runtime.view_runtime_id] = view_runtime

        # start view runtime
        views_logger.debug('starting new view runtime')

        if connection.interactive:
            # If the connection is interactive this method got called
            # by the LonaMessageMiddleware and therefore run in the generic
            # worker pool up this point.
            # To release the worker we have to reschedule to the
            # 'runtime_worker' pool.

            self.server.run_function_async(
                view_runtime.start,
                excutor_name='runtime_worker',
            )

        else:
            return view_runtime.start()

        views_logger.debug('message handled')

    def handle_lona_message(self, connection, window_id, view_runtime_id,
                            method, payload):

        """
        this method gets called by the
        lona.middlewares.LonaMessageMiddleware.process_websocket_message

        """

        # views
        if method == METHOD.VIEW:
            views_logger.debug('view message decoded: %s', repr(payload))

            self.handle_view_message(
                connection=connection,
                window_id=window_id,
                view_runtime_id=view_runtime_id,
                method=method,
                payload=payload,
            )

        # input events
        elif method == METHOD.INPUT_EVENT:
            input_events_logger.debug('event #%s: decoded', payload[0])

            self.handle_input_event_message(
                connection=connection,
                window_id=window_id,
                view_runtime_id=view_runtime_id,
                method=method,
                payload=payload,
            )

        # client error
        elif method == METHOD.CLIENT_ERROR:
            views_logger.debug('client error decoded')

            self.handle_client_error_message(
                connection=connection,
                window_id=window_id,
                view_runtime_id=view_runtime_id,
                method=method,
                payload=payload,
            )
