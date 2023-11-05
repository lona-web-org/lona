from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table

from lona import Bucket


class LonaBucketsCommand:
    """
    List currently open Lona buckets
    """

    NAME = 'lona_buckets'

    def __init__(self, repl):
        self.repl = repl

    def complete(self, text, state, line_buffer):
        server = self.repl.globals['server']
        controller = server._view_runtime_controller

        view_runtime_ids = []

        for view_runtime in controller.iter_view_runtimes():
            view_runtime_ids.append(view_runtime.view_runtime_id)

        view_runtime_ids = sorted(view_runtime_ids)
        candidates = []

        for view_runtime_id in view_runtime_ids:
            if view_runtime_id.startswith(text):
                candidates.append(view_runtime_id)

        candidates.append(None)

        return candidates[state]

    # command #################################################################
    def run(self, argv):

        # parse command line
        argument_parser = ReplArgumentParser(
            repl=self.repl,
            prog='lona_buckets',
        )

        arguments = vars(argument_parser.parse_args(argv[1:]))

        return self.list_buckets(arguments)

    def list_buckets(self, arguments):
        rows = [
            ['Id', 'User', 'Directory', 'URL'],
        ]

        for buckets in Bucket._buckets.values():
            for bucket in buckets.values():
                rows.append([
                    str(bucket.id),
                    str(bucket.request.user),
                    str(bucket.get_path()),
                    str(bucket.get_url()),
                ])

        write_table(rows, self.repl.write)
