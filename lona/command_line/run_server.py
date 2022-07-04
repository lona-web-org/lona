import logging
import asyncio
import socket
import signal
import os

from aiohttp.web import run_app
import aiohttp

from lona.shell.shell import generate_shell_server, embed_shell
from lona.worker_pool import WorkerPool
from lona.logging import setup_logging
from lona.server import LonaServer

AIOHTTP_VERSION = tuple(
    int(part) for part in aiohttp.__version__.split('.')[:2]
)

logger = logging.getLogger('lona')


def run_server(args, server=None):
    loop = asyncio.get_event_loop()

    # setup logging
    log_formatter, log_filter = setup_logging(args)

    # setup lona server
    server = server or LonaServer(
        project_root=args.project_root,
        settings_paths=args.settings,
        settings_pre_overrides=args.settings_pre_overrides,
        settings_post_overrides=args.settings_post_overrides,
    )
    app = server._app

    worker_pool = WorkerPool(
        settings=server.settings,
    )

    async def shutdown(app):
        server = app['lona_server']

        await server.loop.run_in_executor(None, server.worker_pool.shutdown)

    app.on_shutdown.append(shutdown)

    server._loop = loop
    server._worker_pool = worker_pool

    # run server
    if args.shell:
        async def start_shell(server):
            def _start_shell():
                embed_kwargs = {
                    'globals': {
                        'loop': loop,
                        'server': server,
                        'cli_args': vars(args),
                        'log_formatter': log_formatter,
                        'log_filter': log_filter,
                    },
                }

                embed_shell(server=server, **embed_kwargs)

                os.kill(os.getpid(), signal.SIGTERM)

            loop.run_in_executor(None, _start_shell)

        loop.create_task(start_shell(server))

    def _run_app():
        keyword_args = {
            'app': app,
            'host': args.host,
            'port': args.port,
            'shutdown_timeout': args.shutdown_timeout,
        }

        # In aiohttp 3.8 the keyword "loop" was added, which is mandatory if
        # you don’t want aiohttp to start a new event loop but use your
        # previously created one
        if AIOHTTP_VERSION >= (3, 8):
            keyword_args['loop'] = loop

        try:
            run_app(**keyword_args)

        except socket.gaierror as exception:
            if exception.errno not in (-2, ):
                raise

            logger.error('socket.gaierror: %s', exception.args[1])

        except OSError as exception:
            if exception.errno not in (13, 98):
                raise

            logger.error('OSError: %s', exception.args[1])

    if args.shell_server_url:
        embed_kwargs = {
            'bind': args.shell_server_url,
            'globals': {
                'loop': loop,
                'server': server,
                'cli_args': vars(args),
                'log_formatter': log_formatter,
                'log_filter': log_filter,
            },
        }

        repl_server = generate_shell_server(server=server, **embed_kwargs)

        with repl_server:
            _run_app()

    else:
        _run_app()
