from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser
from functools import partial
import asyncio
import logging
import signal
import os

from aiohttp.web import Application, run_app
from jinja2 import Environment
import rlpython

from lona.logging import LogFormatter, LogFilter
from lona.server import LonaServer

try:
    import aiomonitor  # NOQA

    AIOMONITOR = True

except ImportError:
    AIOMONITOR = False


def run_server(args):
    loop = asyncio.get_event_loop()

    # parse command line
    parser = ArgumentParser()

    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--shutdown-timeout', type=float, default=0.0)
    parser.add_argument('-s', '--settings', nargs='+')
    parser.add_argument('-o', '--settings-pre-overrides', nargs='+')
    parser.add_argument('-O', '--settings-post-overrides', nargs='+')
    parser.add_argument('--project-root', type=str, default=os.getcwd())
    parser.add_argument('--shell', action='store_true')
    parser.add_argument('--loggers', type=str, nargs='+')
    parser.add_argument('--monitor', action='store_true')
    parser.add_argument('--monitor-host', type=str, default='localhost')
    parser.add_argument('--monitor-port', type=int, default=50101)
    parser.add_argument('--monitor-console-port', type=int, default=50102)

    parser.add_argument(
        '-l', '--log-level',
        choices=['debug', 'info', 'warn', 'error', 'critical'],
        default='warn',
    )

    cli_args = parser.parse_args(args)

    # setup logging
    logging.basicConfig(level={
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARN,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }[cli_args.log_level.lower()])

    log_formatter = LogFormatter()
    log_filter = LogFilter()

    for handler in logging.getLogger().root.handlers:
        handler.setFormatter(log_formatter)
        handler.addFilter(log_filter)

    if cli_args.loggers:
        for logger_name in cli_args.loggers:
            if logger_name.startswith('_'):
                log_filter.exclude(logger_name[1:])

            else:
                if logger_name.startswith('+'):
                    logger_name = logger_name[1:]

                log_filter.include(logger_name)

    logger = logging.getLogger('lona')

    # setup settings paths
    settings_paths = list(cli_args.settings or [])

    # setup settings overrides
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

    settings_pre_overrides = {}
    settings_post_overrides = {}

    if cli_args.settings_pre_overrides:
        settings_pre_overrides = parse_overrides(
            cli_args.settings_pre_overrides
        )

    if cli_args.settings_post_overrides:
        settings_post_overrides = parse_overrides(
            cli_args.settings_post_overrides
        )

    # setup lona server
    app = Application()

    server = LonaServer(
        app=app,
        project_root=cli_args.project_root,
        settings_paths=settings_paths,
        settings_pre_overrides=settings_pre_overrides,
        settings_post_overrides=settings_post_overrides,
    )

    executor = ThreadPoolExecutor(
        max_workers=server.settings.MAX_WORKERS,
        thread_name_prefix='LonaWorker',
    )

    async def shutdown(app):
        server = app['lona_server']

        await server.loop.run_in_executor(None, server.executor.shutdown)

    app.on_shutdown.append(shutdown)

    server.set_loop(loop)
    server.set_executor(executor)

    # run server
    if cli_args.shell:
        async def start_shell(server):
            def _start_shell():
                rlpython.embed(
                    locals={
                        'server': server,
                    },
                )

                os.kill(os.getpid(), signal.SIGTERM)

            loop.run_in_executor(None, _start_shell)

        loop.create_task(start_shell(server))

    _run_app = partial(
        run_app,
        app=app,
        host=cli_args.host,
        port=cli_args.port,
        shutdown_timeout=cli_args.shutdown_timeout,
    )

    if cli_args.monitor:
        if not AIOMONITOR:
            exit('aiomonitor is not installed')

        monitor_args = {
            'loop': loop,
            'host': cli_args.monitor_host,
            'port': cli_args.monitor_port,
            'console_port': cli_args.monitor_console_port,
            'locals': {
                'server': server,
                'cli_args': vars(cli_args),
                'log_formatter': log_formatter,
                'log_filter': log_filter,
            },
        }

        monitor_class = server.acquire(server.settings.MONITOR_CLASS)

        with monitor_class(**monitor_args):
            _run_app()

    else:
        _run_app()
