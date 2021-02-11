from itertools import chain
from pprint import pformat
import threading
import traceback
import textwrap
import inspect
import sys
import os

from aiomonitor.utils import alt_names
from terminaltables import AsciiTable
from aiomonitor import Monitor

try:
    import IPython

    IPYTHON = True

except ImportError:
    IPYTHON = False

from lona import VERSION_STRING


class LonaMonitor(Monitor):
    prompt = 'lona v{} >>> '.format(VERSION_STRING)

    # helper ##################################################################
    def _gen_borderless_table(self, raw_table_data, pretty=False):
        table_data = []

        for key, value in raw_table_data:
            key = key + ':'

            if pretty:
                value = pformat(value)

            table_data.append(
                [key, value],
            )

        table = AsciiTable(table_data)

        table.inner_column_border = 0
        table.inner_footing_row_border = 0
        table.inner_heading_row_border = 0
        table.inner_row_border = 0
        table.outer_border = 0
        table.padding_left = 0
        table.padding_right = 2

        return table

    def _gen_pformated_table(self, raw_table_data):
        table_header = raw_table_data[0]
        table_data = []

        for key, value in raw_table_data[1:]:
            if isinstance(value, str) and len(value) > 80:
                value = value[0:74] + ' ...'

            table_data.append(
                [key, pformat(value)],
            )

        table_data = sorted(table_data, key=lambda row: row[0])

        return AsciiTable([table_header] + table_data)

    # generic monitor commands ################################################
    def do_locals(self):
        """Show monitor locals"""

        table_data = [['Name', 'Value']]

        for name, value in self._locals.items():
            table_data.append([name, value])

        table = self._gen_pformated_table(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')
        self._sout.flush()

    @alt_names('env')
    def do_unix_env(self, name=None):
        """Show unix environment variables"""

        if name is not None:
            self._sout.write(
                '{}: {}\n'.format(
                    name,
                    os.environ.get(name, '')
                )
            )

            self._sout.flush()

            return

        table_data = [['Name', 'Value']]

        for name, value in os.environ.items():
            table_data.append([name, value])

        table = self._gen_pformated_table(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')
        self._sout.flush()

    @alt_names('ipy')
    def do_ipython(self):
        """Start IPython shell"""

        def _ipython():
            server = self._locals['server']  # NOQA

            IPython.embed()

        if not IPYTHON:
            self._sout.write('ERROR: IPython is not installed\n')
            self._sout.flush()

            return

        self._loop.run_in_executor(None, _ipython)

    # threading commands ######################################################
    def _print_stack(self, frame):
        for line in traceback.format_stack(frame):
            self._sout.write(line)

    def _print_exception(self, exception):
        lines = traceback.format_exception(
            etype=type(exception),
            value=exception,
            tb=exception.__traceback__,
        )

        for line in lines:
            self._sout.write(line)

    @alt_names('tw')
    def do_twhere(self, thread_ident):
        """Show stack of a thread"""

        current_frames = sys._current_frames()

        try:
            thread_ident = int(thread_ident)

        except ValueError:
            pass

        if thread_ident not in current_frames:
            self._sout.write('ERROR: invalid thread id\n')
            self._sout.flush()

            return

        self._print_stack(current_frames[thread_ident])

        self._sout.write('\n')
        self._sout.flush()

    @alt_names('tps')
    def do_tps(self, thread_ident=None):
        """Show thread table"""

        if thread_ident is not None:
            return self.do_twhere(thread_ident)

        current_frames = sys._current_frames()

        # table
        table_data = [['Thread ID', 'Thread Name', 'Alive', 'Daemon', 'Task']]

        for thread in threading.enumerate():
            frame = current_frames[thread.ident]

            # find task
            task = '{}:{} {}'.format(
                frame.f_code.co_filename,
                frame.f_lineno,
                frame.f_code.co_name,
            )

            # append to table
            table_data.append([
                thread.ident,
                thread.getName(),
                thread.isAlive(),
                thread.isDaemon(),
                task,
            ])

        table = AsciiTable(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')
        self._sout.flush()

    # lona state commands #####################################################
    @alt_names('li')
    def do_lona_info(self):
        """Show Lona info"""

        server = self._locals['server']

        self._sout.write('Lona Info\n')
        self._sout.write('=========\n\n')

        table_data = [
            ['Lona version', 'v{}'.format(VERSION_STRING)],
            ['project root', server.project_root],
            ['cli args', pformat(sys.argv)],
        ]

        table = self._gen_borderless_table(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')
        self._sout.flush()

    @alt_names('ls')
    def do_lona_settings(self, name=None):
        """Show Lona settings"""

        server = self._locals['server']

        if name:
            self._sout.write(
                '{} = {}\n'.format(
                    name,
                    repr(server.settings.get(name, None))
                )
            )

            self._sout.flush()

            return

        self._sout.write('Lona Settings\n')
        self._sout.write('=============\n\n')

        table_data = [['Name', 'Value']]

        for key in list(server.settings):
            table_data.append(
                [key, server.settings.get(key)],
            )

        table = self._gen_pformated_table(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')
        self._sout.flush()

    @alt_names('lc')
    def do_lona_connections(self, name=None):
        """Show current Lona websocket connections"""

        server = self._locals['server']

        self._sout.write('Lona Connections\n')
        self._sout.write('================\n\n')

        table_data = [['User', 'URL']]

        for connection in server.websocket_connections:
            table_data.append(
                [repr(connection.user), connection.http_request.url.path],
            )

        table = AsciiTable(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')
        self._sout.flush()

    @alt_names('lss')
    def do_lona_server_state(self):
        """Show Lona server state"""

        server = self._locals['server']

        self._sout.write('Lona Server State\n')
        self._sout.write('=================\n\n')

        table_data = [['Name', 'Value']]

        with server.state.lock:
            for key, value in server.state.items():
                table_data.append(
                    [repr(key), repr(value)],
                )

        table = AsciiTable(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')
        self._sout.flush()

    # lona routes #############################################################
    @alt_names('lr')
    def do_lona_routes(self, route_id=None):
        """Show Lona routes"""

        server = self._locals['server']

        if route_id:
            try:
                route_id = int(route_id)

                self._sout.write(
                    '{}\n'.format(repr(server.router.routes[route_id])))

                self._sout.flush()

                return

            except Exception:
                self._sout.write('ERROR: Invalid route id\n')
                self._sout.flush()

                return

        self._sout.write('Lona Routes\n')
        self._sout.write('===========\n\n')

        table_data = [['Route ID', 'Route']]

        for index, route in enumerate(server.router.routes):
            table_data.append(
                [index, repr(route)],
            )

        table = AsciiTable(table_data)

        table.justify_columns[0] = 'right'

        self._sout.write(table.table)
        self._sout.write('\n\n')
        self._sout.flush()

    @alt_names('lru')
    def do_lona_resolve_url(self, path):
        """Resolve Lona URL"""

        server = self._locals['server']

        match, route, match_info = server.router.resolve(path)

        if not match:
            self._sout.write('No match\n')
            self._sout.flush()

            return

        route_id = server.router.routes.index(route)

        table_data = [
            ['Route ID:', route_id],
            ['Route:', repr(route)],
            ['Match info:', repr(match_info)],
        ]

        table = self._gen_borderless_table(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')
        self._sout.flush()

    # lona view commands ######################################################
    def _get_view_path(self, view_runtime):
        if view_runtime.view.__module__.endswith('.py'):
            return view_runtime.view.__module__

        return inspect.getabsfile(view_runtime.view)

    def _get_view_name(self, view_runtime):
        if view_runtime.view_spec.is_class_based:
            return view_runtime.view.__class__.__name__

        return view_runtime.view.__name__

    def _get_shortened_stack(self, thread_ident, path):
        frame = sys._current_frames()[thread_ident]

        # frame summary list
        frame_summary_list = traceback.extract_stack(frame)

        while len(frame_summary_list) > 0:
            if frame_summary_list[0].filename == path:
                break

            frame_summary_list.pop(0)

        while len(frame_summary_list) > 0:
            if frame_summary_list[-1].filename == path:
                break

            frame_summary_list.pop(-1)

        # frame list
        frame_list = []

        while frame.f_back is not None:
            frame_list.insert(0, frame)
            frame = frame.f_back

        while len(frame_list) > 0:
            if frame_list[0].f_code.co_filename == path:
                break

            frame_list.pop(0)

        while len(frame_list) > 0:
            if frame_list[-1].f_code.co_filename == path:
                break

            frame_list.pop(-1)

        return frame_summary_list, frame_list

    @alt_names('lvi')
    def do_lona_view_info(self, view_id):
        """Show info of Lona view"""

        server = self._locals['server']
        controller = server.view_runtime_controller

        try:
            view_runtime = controller.get_view_runtime(int(view_id))

        except Exception:
            view_runtime = None

        if not view_runtime:
            self._sout.write('ERROR: invalid view id\n\n')
            self._sout.flush()

            return

        # runtime info
        self._sout.write('Runtime Info\n')
        self._sout.write('============\n')

        path = self._get_view_path(view_runtime)
        name = self._get_view_name(view_runtime)

        table_data = [
            ['Thread ID', view_runtime.thread_ident],
            ['View ID', view_runtime.view_runtime_id],
            ['Multi user', repr(isinstance(view_runtime.request.user, list))],
            ['Daemon', repr(view_runtime.is_daemon)],
            ['Started at', str(view_runtime.started_at)],
            ['Stopped at', str(view_runtime.stopped_at or '-')],
            ['State', view_runtime.state],
        ]

        table = self._gen_borderless_table(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')

        # view info
        self._sout.write('View Info\n')
        self._sout.write('=========\n')

        table_data = [
            ['Name', name],
            ['Path', path],
            ['User', repr(view_runtime.request.user)],
            ['Route', repr(view_runtime.route)],
            ['Match info', repr(view_runtime.match_info)],
            ['Method', repr(view_runtime.request.method)],
            ['GET Data', pformat(view_runtime.request.GET)],
            ['POST Data', pformat(view_runtime.request.POST)],
        ]

        table = self._gen_borderless_table(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')

        # connections
        self._sout.write('Connections\n')
        self._sout.write('===========\n')

        table_data = [['User', 'Connection', 'Window ID', 'URL']]

        for connection, (window_id, url) in view_runtime.connections.items():
            table_data.append([
                repr(connection.user),
                repr(connection),
                window_id,
                repr(url),
            ])

        table = AsciiTable(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')

        # crash report
        if view_runtime.state == view_runtime.STATE.CRASHED:
            self._sout.write('Crash Report\n')
            self._sout.write('============\n')

            self._print_exception(view_runtime.stop_reason)

        # shortened stack
        elif(view_runtime.state > 20 and
             view_runtime.state < 30):

            self._sout.write('Shortened Stack\n')
            self._sout.write('===============\n')

            frame_summary_list, frame_list = \
                self._get_shortened_stack(view_runtime.thread_ident, path)

            for line in traceback.format_list(frame_summary_list):
                self._sout.write(line)

        self._sout.write('\n')
        self._sout.flush()

    @alt_names('lvm')
    def do_lona_view_memory(self, view_id):
        """Show memory of Lona view"""

        server = self._locals['server']
        controller = server.view_runtime_controller

        try:
            view_runtime = controller.get_view_runtime(int(view_id))

        except Exception:
            view_runtime = None

        if not view_runtime:
            self._sout.write('ERROR: invalid view id\n')
            self._sout.flush()

            return

        path = self._get_view_path(view_runtime)

        frame_summary_list, frame_list = \
            self._get_shortened_stack(view_runtime.thread_ident, path)

        self._sout.write('View Memory\n')
        self._sout.write('===========\n\n')

        for index, frame_summary in enumerate(frame_summary_list):
            frame = frame_list[index]

            for line in traceback.format_list([frame_summary]):
                self._sout.write(textwrap.dedent(line))

            table_data = []

            for key, value in frame.f_locals.items():
                table_data.append([key, value])

            table = self._gen_borderless_table(table_data, pretty=True)

            self._sout.write('\n')
            self._sout.write(textwrap.indent(table.table, prefix='    '))
            self._sout.write('\n\n')

        self._sout.flush()

    @alt_names('lv')
    def do_lona_views(self, view_id=None):
        """Show running Lona views"""

        if view_id is not None:
            return self.do_lona_view_info(view_id)

        self._sout.write('Running Lona Views\n')
        self._sout.write('==================\n\n')

        server = self._locals['server']
        controller = server.view_runtime_controller

        view_runtimes = chain(
            controller.iter_multi_user_view_runtimes(),
            controller.iter_single_user_view_runtimes(),
        )

        table_data = [
            ['Runtime ID', 'Thread ID', 'Flags', 'User', 'Route ID',
             'URL', 'State'],
        ]

        for view_runtime in view_runtimes:
            # find route id
            route = view_runtime.route

            if route:
                route_id = server.router.routes.index(view_runtime.route)

                url = route.format_string.format(
                    **view_runtime.request.match_info)

            else:
                # in case of 404 or 500 responses the runtime
                # may have no route set

                route_id = ''
                url = ''

            # flags
            flags = ''

            if isinstance(view_runtime.request.user, list):
                flags += 'M'

            if view_runtime.is_daemon:
                flags += 'D'

            # add table row
            table_data.append([
                str(view_runtime.view_runtime_id),
                view_runtime.thread_ident,
                flags,
                repr(view_runtime.request.user),
                route_id,
                url,
                view_runtime.state,
            ])

        table = AsciiTable(table_data)

        self._sout.write(table.table)
        self._sout.write('\n\n')
        self._sout.flush()
