from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table


class LonaConnectionsCommand:
    """
    List all current connections to Lona
    """

    NAME = 'lona_connections'

    def __init__(self, repl):
        self.repl = repl

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(
            repl=self.repl, prog='lona_connections')

        argument_parser.parse_args(argv[1:])

        server = self.repl.locals['server']

        # write connections
        rows = [['User', 'URL']]

        for connection in server.websocket_connections:
            rows.append(
                [repr(connection.user), connection.http_request.url.path],
            )

        write_table(rows, self.repl.write)
