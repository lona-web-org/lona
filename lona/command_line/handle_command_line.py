from argparse import RawTextHelpFormatter, ArgumentParser
import logging
import os

from watchfiles import run_process
from jinja2 import Environment

from lona.command_line.collect_static import collect_static
from lona.command_line.run_server import run_server
from lona import VERSION_STRING

logger = logging.getLogger('lona')

DESCRIPTION = f"""
Lona {VERSION_STRING}
Documentation: lona-web.org
Code: https://github.com/lona-web-org/lona
""".strip()

EPILOG = """\
You can set environment variables LONA_DEFAULT_HOST and LONA_DEFAULT_PORT,
to override built-in defaults ('localhost' resp. '8080').
""".rstrip()


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


def handle_command_line(argv):
    parser = ArgumentParser(
        prog='lona',
        formatter_class=RawTextHelpFormatter,
        description=DESCRIPTION,
    )

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
        default='info',
    )

    parser_run_server.add_argument(
        '--loggers',
        type=str,
        nargs='+',
    )

    parser_run_server.add_argument(
        '--debug-mode',
        choices=['messages', 'views', 'input-events', 'view-events'],
    )

    parser_run_server.add_argument(
        '--syslog-priorities',
        choices=['no', 'auto', 'always'],
        default='auto',
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
        default=os.environ.get('LONA_DEFAULT_HOST', 'localhost'),
    )

    parser_run_server.add_argument(
        '--port',
        type=int,
        default=os.environ.get('LONA_DEFAULT_PORT', '8080'),
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

    parser_run_server.add_argument(
        '--live-reload',
        action='store_true',
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
        choices=['messages', 'views', 'input-events', 'view-events'],
    )

    parser_collect_static.add_argument(
        '--syslog-priorities',
        choices=['no', 'auto', 'always'],
        default='auto',
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

    args.settings_pre_overrides = parse_overrides(
        args.settings_pre_overrides,
    )

    args.settings_post_overrides = parse_overrides(
        args.settings_post_overrides,
    )

    # run
    if args.command == 'run-server':
        if args.live_reload:
            run_process(
                args.project_root,
                target=run_server,
                args=(args, ),
            )

        else:
            run_server(args)

    elif args.command == 'collect-static':
        collect_static(args)
