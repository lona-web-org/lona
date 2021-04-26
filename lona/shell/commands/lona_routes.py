from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table
from rlpython.utils.attribute_table import write_attribute_table


class LonaRoutesCommand:
    """
    List and test Lona routes
    """

    NAME = 'lona_routes'

    def __init__(self, repl):
        self.repl = repl

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(
            repl=self.repl,
            prog='lona_routes',
        )

        argument_parser.add_argument('route-id', nargs='?')
        argument_parser.add_argument('-r', '--resolve', type=str)

        arguments = vars(argument_parser.parse_args(argv[1:]))

        server = self.repl.locals['server']

        # resolve
        if arguments['resolve']:
            path = arguments['resolve']
            match, route, match_info = server.router.resolve(path)

            if not match:
                self.repl.write('No match')

                return

            route_id = server.router.routes.index(route)

            rows = [
                ['Route ID', route_id],
                ['Route', repr(route)],
                ['Match info', repr(match_info)],
            ]

            write_attribute_table(rows, self.repl.write)

            return

        # show given route
        if arguments['route-id']:
            try:
                route_id = int(arguments['route-id'])

                self.repl.write(repr(server.router.routes[route_id]) + '\n')

                return

            except Exception:
                self.repl.write_error('invalid route id\n')

                return 1

        # show all routes
        rows = [['Route ID', 'Route']]

        for index, route in enumerate(server.router.routes):
            rows.append([index, repr(route)])

        write_table(rows, self.repl.write)
