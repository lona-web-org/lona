import asyncio
import logging
import signal
import socket
import os

from aiohttp.web import Application, run_app

from lona.shell.shell import embed_shell, generate_shell_server
from lona.worker_pool import WorkerPool
from lona.logging import setup_logging
from lona.server import LonaServer

logger = logging.getLogger('lona')


def run_server(args, app=None, server=None):
    loop = asyncio.get_event_loop()

    # setup logging
    log_formatter, log_filter = setup_logging(args)

    # setup lona server
    app = app or Application()

    server = server or LonaServer(
        app=app,
        project_root=args.project_root,
        settings_paths=args.settings,
        settings_pre_overrides=args.settings_pre_overrides,
        settings_post_overrides=args.settings_post_overrides,
    )

    worker_pool = WorkerPool(
        settings=server.settings,
    )

    async def shutdown(app):
        server = app['lona_server']

        await server.loop.run_in_executor(None, server.worker_pool.shutdown)

    app.on_shutdown.append(shutdown)

    server.set_loop(loop)
    server.set_worker_pool(worker_pool)

    # run server
    if args.shell:
        async def start_shell(server):
            def _start_shell():
                embed_kwargs = {
                    'locals': {
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
        try:
            run_app(
                app=app,
                host=args.host,
                port=args.port,
                shutdown_timeout=args.shutdown_timeout,
            )

        except socket.gaierror as exception:
            if exception.errno not in (-2, ):
                raise

            logger.error('socket.gaierror: ' + exception.args[1])

        except OSError as exception:
            if exception.errno not in (13, 98):
                raise

            logger.error('OSError: ' + exception.args[1])

    if args.shell_server_url:
        embed_kwargs = {
            'bind': args.shell_server_url,
            'locals': {
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
