from itertools import chain
from pprint import pformat
import traceback
import textwrap
import inspect
import sys

from rlpython.utils.attribute_table import write_attribute_table
from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table

from lona.symbols import VIEW_RUNTIME_STATE


class LonaViewsCommand:
    """
    List currently running Lona views
    """

    NAME = 'lona_views'

    def __init__(self, repl):
        self.repl = repl

    def complete(self, text, state, line_buffer):
        server = self.repl.locals['server']
        controller = server.view_runtime_controller

        view_runtimes = chain(
            controller.iter_multi_user_view_runtimes(),
            controller.iter_single_user_view_runtimes(),
        )

        view_runtime_ids = []

        for view_runtime in view_runtimes:
            view_runtime_ids.append(str(view_runtime.view_runtime_id))

        view_runtime_ids = sorted(view_runtime_ids)
        candidates = []

        for view_runtime_id in view_runtime_ids:
            if view_runtime_id.startswith(text):
                candidates.append(view_runtime_id)

        candidates.append(None)

        return candidates[state]

    # helper ##################################################################
    def _get_view_path(self, view_runtime):
        if view_runtime.view.__module__.endswith('.py'):
            return view_runtime.view.__module__

        return inspect.getabsfile(view_runtime.view)

    def _get_view_name(self, view_runtime):
        return view_runtime.view.__class__.__name__

    def _print_exception(self, exception):
        lines = traceback.format_exception(
            etype=type(exception),
            value=exception,
            tb=exception.__traceback__,
        )

        for line in lines:
            self.repl.write(line)

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

    # command #################################################################
    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(repl=self.repl, prog='lona_views')

        argument_parser.add_argument('runtime-id', nargs='?')
        argument_parser.add_argument('-m', '--memory', action='store_true')

        arguments = vars(argument_parser.parse_args(argv[1:]))

        if arguments['memory']:
            return self.show_view_memory(arguments)

        if arguments['runtime-id']:
            return self.show_view_info(arguments)

        return self.list_views(arguments)

    def show_view_memory(self, arguments):
        server = self.repl.locals['server']
        controller = server.view_runtime_controller

        if not arguments['runtime-id']:
            self.repl.write_error('no runtime id given')

            return 1

        try:
            view_runtime = controller.get_view_runtime(
                view_runtime_id=int(arguments['runtime-id']),
            )

        except Exception:
            view_runtime = None

        if not view_runtime:
            self.repl.write_error('invalid runtime id\n')

            return 1

        path = self._get_view_path(view_runtime)

        frame_summary_list, frame_list = \
            self._get_shortened_stack(view_runtime.thread_ident, path)

        self.repl.write('View Memory\n')
        self.repl.write('===========\n\n')

        for index, frame_summary in enumerate(frame_summary_list):
            frame = frame_list[index]

            for line in traceback.format_list([frame_summary]):
                self.repl.write(textwrap.dedent(line))

            rows = [['Key', 'Value']]

            for key, value in frame.f_locals.items():
                rows.append([key, pformat(value)])

            write_table(rows, self.repl.write)
            self.repl.write('\n\n')

    def show_view_info(self, arguments):
        server = self.repl.locals['server']
        controller = server.view_runtime_controller

        try:
            view_runtime = controller.get_view_runtime(
                view_runtime_id=int(arguments['runtime-id']),
            )

        except Exception:
            view_runtime = None

        if not view_runtime:
            self.repl.write_error('invalid runtime id\n')

            return 1

        # runtime info
        self.repl.write('Runtime Info\n')
        self.repl.write('============\n')

        path = self._get_view_path(view_runtime)
        name = self._get_view_name(view_runtime)

        rows = [
            ['Thread ID', view_runtime.thread_ident],
            ['Thread Name', view_runtime.thread_name],
            ['View ID', view_runtime.view_runtime_id],
            ['Multi user', repr(isinstance(view_runtime.request.user, list))],
            ['Daemon', repr(view_runtime.is_daemon)],
            ['Started at', str(view_runtime.started_at)],
            ['Stopped at', str(view_runtime.stopped_at or '-')],
            ['State', view_runtime.state],
        ]

        write_attribute_table(rows, self.repl.write)
        self.repl.write('\n')

        # view info
        self.repl.write('View Info\n')
        self.repl.write('=========\n')

        rows = [
            ['Name', name],
            ['Path', path],
            ['User', repr(view_runtime.request.user)],
            ['Route', repr(view_runtime.route)],
            ['Match info', repr(view_runtime.match_info)],
            ['Method', repr(view_runtime.request.method)],
            ['GET Data', pformat(view_runtime.request.GET)],
            ['POST Data', pformat(view_runtime.request.POST)],
        ]

        write_attribute_table(rows, self.repl.write)
        self.repl.write('\n')

        # connections
        self.repl.write('Connections\n')
        self.repl.write('===========\n')

        rows = [['User', 'Connection', 'Window ID', 'URL']]

        for connection, (window_id, url) in view_runtime.connections.items():
            rows.append([
                repr(connection.user),
                repr(connection),
                window_id,
                repr(url),
            ])

        write_attribute_table(rows, self.repl.write)
        self.repl.write('\n')

        # crash report
        if view_runtime.state == VIEW_RUNTIME_STATE.CRASHED:
            self.repl.write('Crash Report\n')
            self.repl.write('============\n')

            self._print_exception(view_runtime.stop_reason)

        # shortened stack
        elif(view_runtime.state > 20 and
             view_runtime.state < 30):

            self.repl.write('Shortened Stack\n')
            self.repl.write('===============\n')

            frame_summary_list, frame_list = \
                self._get_shortened_stack(view_runtime.thread_ident, path)

            for line in traceback.format_list(frame_summary_list):
                self.repl.write(line)

        self.repl.write('\n')

    def list_views(self, arguments):
        server = self.repl.locals['server']
        controller = server.view_runtime_controller

        view_runtimes = chain(
            controller.iter_multi_user_view_runtimes(),
            controller.iter_single_user_view_runtimes(),
        )

        rows = [
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
            rows.append([
                str(view_runtime.view_runtime_id),
                view_runtime.thread_ident,
                flags,
                repr(view_runtime.request.user),
                route_id,
                url,
                view_runtime.state,
            ])

        write_table(rows, self.repl.write)
