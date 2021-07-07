from argparse import ArgumentParser, RawTextHelpFormatter
import logging
import sys
import os

from jinja2 import Environment

from lona.command_line.collect_static import collect_static
from lona.command_line.run_server import run_server
from lona import VERSION_STRING

logger = logging.getLogger('lona')

DESCRIPTION = """
Lona {}
Documentation: lona-web.org
Code: github.com/fscherf/lona
""".format(VERSION_STRING).strip()


def handle_command_line(argv):
    parser = ArgumentParser(
        prog='lona',
        formatter_class=RawTextHelpFormatter,
        description=DESCRIPTION,
    )

    # the keyword 'required' is not available in python versions lower than 3.7
    if sys.version_info < (3, 7):
        sub_parsers = parser.add_subparsers(
            dest='command',
        )

    else:
        sub_parsers = parser.add_subparsers(
            dest='command',
            required=True,
        )

    # run-server ##############################################################
    parser_run_server = sub_parsers.add_parser(
        'run-server',
    )

    # logging
    parser_run_server.add_argument(
        '-l',
        '--log-level',
        choices=['debug', 'info', 'warn', 'error', 'critical'],
        default='warn',
    )

    parser_run_server.add_argument(
        '--loggers',
        type=str,
        nargs='+',
    )

    parser_run_server.add_argument(
        '--debug-mode',
        choices=['messages', 'views', 'input-events'],
    )

    # settings
    parser_run_server.add_argument(
        '--project-root',
        type=str,
        default=os.getcwd(),
    )

    parser_run_server.add_argument(
        '-s',
        '--settings',
        nargs='+',
        default=[],
    )

    parser_run_server.add_argument(
        '-o',
        '--settings-pre-overrides',
        nargs='+',
        default=[],
    )

    parser_run_server.add_argument(
        '-O',
        '--settings-post-overrides',
        nargs='+',
        default=[],
    )

    # custom
    parser_run_server.add_argument(
        '--host',
        type=str,
        default='localhost',
    )

    parser_run_server.add_argument(
        '--port',
        type=int,
        default=8080,
    )

    parser_run_server.add_argument(
        '--shutdown-timeout',
        type=float,
        default=0.0,
    )

    parser_run_server.add_argument(
        '--shell',
        action='store_true',
    )

    parser_run_server.add_argument(
        '--shell-server-url',
        type=str,
        default='',
    )

    # collect-static ##########################################################
    parser_collect_static = sub_parsers.add_parser(
        'collect-static',
    )

    # logging
    parser_collect_static.add_argument(
        '-l',
        '--log-level',
        choices=['debug', 'info', 'warn', 'error', 'critical'],
        default='warn',
    )

    parser_collect_static.add_argument(
        '--loggers',
        type=str,
        nargs='+',
    )

    parser_collect_static.add_argument(
        '--debug-mode',
        choices=['messages', 'views', 'input-events'],
    )

    # settings
    parser_collect_static.add_argument(
        '--project-root',
        type=str,
        default=os.getcwd(),
    )

    parser_collect_static.add_argument(
        '-s',
        '--settings',
        nargs='+',
        default=[],
    )

    parser_collect_static.add_argument(
        '-o',
        '--settings-pre-overrides',
        nargs='+',
        default=[],
    )

    parser_collect_static.add_argument(
        '-O',
        '--settings-post-overrides',
        nargs='+',
        default=[],
    )

    # custom
    parser_collect_static.add_argument(
        'destination',
    )

    parser_collect_static.add_argument(
        '--clean',
        action='store_true',
        default=False,
    )

    parser_collect_static.add_argument(
        '--silent',
        action='store_true',
        default=False,
    )

    parser_collect_static.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
    )

    # parse argv
    args = parser.parse_args(argv[1:])

    # this can happen on python versions lower than 3.7
    if not args.command:
        exit('no sub command was given')

    def parse_overrides(raw_overrides):
        environment = Environment()
        overrides = {}

        for override in raw_overrides:
            if '=' not in override:
                logger.error(
                    "settings overrides: invalid format: '%s'", override)

                continue

            name, value = override.split('=', 1)
            value = environment.compile_expression(value)()

            overrides[name] = value

        return overrides

    args.settings_pre_overrides = parse_overrides(
        args.settings_pre_overrides,
    )

    args.settings_post_overrides = parse_overrides(
        args.settings_post_overrides,
    )

    # run
    if args.command == 'run-server':
        run_server(args)

    elif args.command == 'collect-static':
        collect_static(args)
