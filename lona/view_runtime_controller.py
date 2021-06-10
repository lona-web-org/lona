import logging

from yarl import URL

from lona.protocol import encode_http_redirect, METHOD
from lona.view_runtime import ViewRuntime
from lona.exceptions import ServerStop
from lona.types import Mapping

logger = logging.getLogger('lona.view_runtime_controller')
input_events_logger = logging.getLogger('lona.input_events')


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
        return

    def stop(self):
        # running views per user
        for user, view_runtimes in self.running_single_user_views.items():
            for view_runtime in view_runtimes.copy():
                view_runtime.stop(reason=ServerStop)

        # multi user views
        for route, view in self.running_multi_user_views.items():
            view.stop(reason=ServerStop)

    # helper ##################################################################
    def iter_single_user_view_runtimes(self):
        # this method is not thread safe
        # only for debug purposes
        # yields: view_runtime

        running_single_user_views = self.running_single_user_views.copy()

        for user, view_runtimes in running_single_user_views.items():
            for view_runtime in view_runtimes.copy():
                yield view_runtime

    def iter_multi_user_view_runtimes(self):
        # this method is not thread safe
        # only for debug purposes
        # yields: view_runtime

        running_multi_user_views = self.running_multi_user_views.copy()

        for route, view_runtime in running_multi_user_views.items():
            yield view_runtime

    def get_view_runtime(self, view_runtime_id):
        # this method is not thread safe
        # only for debug purposes
        # yields: view_runtime

        # multi user view runtimes
        for view_runtime in self.iter_multi_user_view_runtimes():
            if view_runtime.view_runtime_id == view_runtime_id:
                return view_runtime

        # single user view runtimes
        for view_runtime in self.iter_single_user_view_runtimes():
            if view_runtime.view_runtime_id == view_runtime_id:
                return view_runtime

    def get_running_views_count(self, user):
        if user not in self.running_single_user_views:
            return 0

        count = 0

        for view_runtime in self.running_single_user_views[user]:
            if not view_runtime.frontend and not view_runtime.is_stopped:
                count += 1

        return count

    def view_is_already_running(self, request):
        if request.user in self.running_single_user_views:
            for view_runtime in self.running_single_user_views[request.user]:
                if(view_runtime.route == request.route and
                   view_runtime.match_info == request.match_info and
                   view_runtime.is_daemon):

                    return True

        return False

    # view management #########################################################
    def remove_connection(self, connection, window_id=None):
        for user, view_runtimes in self.running_single_user_views.items():
            for view_runtime in view_runtimes:
                view_runtime.remove_connection(connection, window_id=window_id)

        for route, view in self.running_multi_user_views.items():
            view.remove_connection(connection, window_id=window_id)

    def remove_view_runtime(self, view_runtime):
        user = view_runtime.start_connection.user

        self.running_single_user_views[user].remove(view_runtime)

    # lona messages ###########################################################
    def handle_lona_message(self, connection, window_id, view_runtime_id,
                            method, payload):

        """
        this method gets called by the
        lona.middlewares.LonaMessageMiddleware.process_websocket_message

        """

        # views
        if method == METHOD.VIEW:
            url, post_data = payload

            url_object = URL(url)

            # disconnect client window from previous view
            self.remove_connection(connection, window_id)

            # resolve url
            match, route, match_info = self.server.router.resolve(
                url_object.path)

            # route is not interactive; issue a http redirect
            if match and (route.http_pass_through or not route.interactive):
                message = encode_http_redirect(
                    window_id=window_id,
                    view_runtime_id=None,
                    target_url=url,
                )

                connection.send_str(message)

                return

            view_runtime = ViewRuntime(
                server=self.server,
                url=url,
                route=route,
                match_info=match_info,
                post_data=post_data or {},
                start_connection=connection,
            )

            view_runtime.add_connection(
                connection=connection,
                window_id=window_id,
                url=url,
            )

            response_dict = view_runtime.run_middlewares(
                connection=connection,
                window_id=window_id,
                url=url,
            )

            # request got handled by a middleware
            if response_dict:
                return

            # check for 403 forbidden error
            response_dict = view_runtime.run_user_enter(
                connection=connection,
                window_id=window_id,
                url=url,
            )

            if response_dict:
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
                    running_view_runtime.reconnect_connection(
                        connection=connection,
                        window_id=window_id,
                        url=url,
                    )

                    return

                else:
                    running_view_runtime.stop()

            # connect to a multi user view
            elif(route in self.running_multi_user_views):
                self.running_multi_user_views[route].reconnect_connection(
                    connection=connection,
                    window_id=window_id,
                    url=url,
                )

                return

            # start view
            if user not in self.running_single_user_views:
                self.running_single_user_views[user] = []

            self.running_single_user_views[user].append(view_runtime)

            self.server.run_function_async(
                view_runtime.start,
                excutor_name='runtime_worker',
            )

        # input events
        elif method == METHOD.INPUT_EVENT:
            input_events_logger.debug('event #%s: decoded', payload[0])

            user = connection.user

            if user not in self.running_single_user_views:
                input_events_logger.debug(
                    'event #%s: user is unknown. event is skipped',
                    payload[0],
                )

                return

            for view_runtime in self.running_single_user_views[user]:
                if view_runtime.view_runtime_id == view_runtime_id:
                    input_events_logger.debug(
                        'event #%s: is handled by runtime #%s',
                        payload[0],
                        view_runtime_id,
                    )

                    view_runtime.handle_input_event(connection, payload)

                    return

            input_events_logger.debug(
                'event #%s: runtime id is unknown. event is skipped',
                payload[0],
            )
