import os

from rlpython.utils.argument_parser import ReplArgumentParser


class LonaStaticFilesCommand:
    """
    List all loaded static files
    """

    NAME = 'lona_static_files'

    def __init__(self, repl):
        self.repl = repl

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(
            repl=self.repl,
            prog='lona_static_files',
            description=self.__doc__,
        )

        argument_parser.add_argument('static-dir', nargs='?')

        argument_parser.add_argument(
            '-l',
            '--list-directories',
            action='store_true',
        )

        argument_parser.add_argument(
            '-r',
            '--resolve',
        )

        args = argument_parser.parse_args(argv[1:])

        server = self.repl.locals['server']

        # resolve
        if args.resolve:
            abs_path = server.static_file_loader.resolve_path(args.resolve)

            if not abs_path:
                return 1

            self.repl.write('{}\n'.format(abs_path))

            return

        # list directories
        if args.list_directories:
            for static_dir in server.static_file_loader.static_dirs:
                self.repl.write('{}\n'.format(static_dir))

            return

        # list static files
        static_files = {}

        for static_dir in server.static_file_loader.static_dirs:
            for root, dirs, files in os.walk(static_dir):
                for _file in files:
                    name = os.path.join(root, _file)

                    if name in static_files:
                        continue

                    static_files[name] = static_dir

        static_file_list = []

        for name, static_dir in static_files.items():
            static_file_list.append(os.path.join(static_dir, name))

        static_file_list.sort()

        for static_file in static_file_list:
            self.repl.write('{}\n'.format(static_file))
