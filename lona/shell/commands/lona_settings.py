from pprint import pformat

from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table


class LonaSettingsCommand:
    """
    List currently loaded Lona settings
    """

    NAME = 'lona_settings'

    def __init__(self, repl):
        self.repl = repl

    def complete(self, text, state, line_buffer):
        names = sorted(list(self.repl.locals['server'].settings))
        candidates = []

        for name in names:
            if name.startswith(text):
                candidates.append(name)

        candidates.append(None)

        return candidates[state]

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(
            repl=self.repl,
            prog='lona_settings',
        )

        argument_parser.add_argument('name', nargs='?')

        arguments = vars(argument_parser.parse_args(argv[1:]))

        server = self.repl.locals['server']

        # write setting
        if arguments['name']:
            self.repl.write(
                pformat(server.settings.get(arguments['name'], None)) + '\n',
            )

            return 0

        # write all settings
        rows = [['Name', 'Value']]

        for key in list(server.settings):
            rows.append(
                [key, pformat(server.settings.get(key))],
            )

        write_table(rows, self.repl.write)
