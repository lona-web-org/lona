from pprint import pformat

from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table


class LonaServerStateCommand:
    """
    Show current server.state
    """

    NAME = 'lona_server_state'

    def __init__(self, repl):
        self.repl = repl

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(
            repl=self.repl, prog='lona_server_state')

        argument_parser.parse_args(argv[1:])

        server = self.repl.locals['server']

        # write table
        rows = [['Key', 'Value']]

        with server.state.lock:
            for key, value in server.state.items():
                rows.append(
                    [pformat(key), pformat(value)],
                )

        if len(rows) == 1:
            return

        write_table(rows, self.repl.write)
