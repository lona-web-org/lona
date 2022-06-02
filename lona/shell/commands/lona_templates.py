import os

from rlpython.utils.argument_parser import ReplArgumentParser
from jinja2.exceptions import TemplateNotFound


class LonaTemplatesCommand:
    """
    List all templates
    """

    NAME = 'lona_templates'

    def __init__(self, repl):
        self.repl = repl

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(
            repl=self.repl,
            prog='lona_templates',
            description=self.__doc__,
        )

        argument_parser.add_argument('template-dir', nargs='?')

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

        server = self.repl.globals['server']

        # resolve
        if args.resolve:
            try:
                template = server.get_template(args.resolve)

            except TemplateNotFound:
                return 1

            self.repl.write(f'{template.filename}\n')

            return

        # list directories
        if args.list_directories:
            for static_dir in server.template_dirs:
                self.repl.write(f'{static_dir}\n')

            return

        # list static files
        templates = {}

        for template_dir in server.template_dirs:
            for root, _dirs, files in os.walk(template_dir):
                for _file in files:
                    name = os.path.join(root, _file)

                    if name in templates:
                        continue

                    templates[name] = template_dir

        template_list = []

        for name, static_dir in templates.items():
            template_list.append(os.path.join(static_dir, name))

        template_list.sort()

        for static_file in template_list:
            self.repl.write(f'{static_file}\n')
