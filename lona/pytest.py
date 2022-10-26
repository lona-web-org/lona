from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Callable
from typing import AsyncContextManager, Dict, cast, Any
from asyncio import AbstractEventLoop, Future, sleep
from contextlib import asynccontextmanager
from dataclasses import dataclass
import webbrowser as _webbrowser
import time
import os

from aiohttp.test_utils import TestClient
from aiohttp.web import Application
import pytest

from lona.shell.shell import embed_shell
from lona.worker_pool import WorkerPool
from lona.server import LonaServer
from lona import LonaApp


@dataclass
class LonaContext:
    client: TestClient
    app: None | LonaApp
    server: LonaServer
    event_loop: AbstractEventLoop

    def make_url(self, path: str = '') -> str:
        """
        Takes a path and returns a full URL to the running test server.

        This method is necessary because the Lona pytest plugin spins up a test
        server that runs on an unprivileged random port, so URLs are not stable
        between test runs.

        :path: (str) path to to view
        """

        return str(self.client.make_url(path))

    def debug_interactive(
            self,
            webbrowser: bool = True,
            sync: bool = False,
            locals: Dict[str, Any] | None = None,
    ) -> Future | None:  # pragma: no cover

        """
        This method pauses the current test by starting an rlpython shell and
        starts a webbrowser that points to the currently running test server.
        The test continues when the rlpython shell is exited.

        Async Example:

            async def test_my_feature(lona_app_context):
                context = await lona_app_context(setup_app)

                await context.debug_interactive(locals=locals())

        Sync Example:

            async def test_my_feature(lona_app_context):
                context = await lona_app_context(setup_app)

                def run_test():
                    context.debug_interactive(
                        sync=True,
                        locals=locals(),
                    )

                context.event_loop.run_in_executor(None, run_test)

        :webbrowser: (bool) start a webbrowser that points to the test server
        :sync:       (bool) run blocking in the current thread
        :locals:     (dict|None) variable overrides for the rlpython shell
        """

        def _debug_interactive():
            # start browser
            if webbrowser:
                os.environ['DISPLAY'] = ':0'
                _webbrowser.open(self.make_url())

            # embed shell
            _locals = locals or {}

            _locals = {
                'server': self.server,
                'lona_context': self,
                **_locals,
            }

            embed_shell(
                server=self.server,
                locals=_locals,
            )

        if sync:
            _debug_interactive()

            return None

        return self.event_loop.run_in_executor(None, _debug_interactive)


@pytest.fixture()
def lona_app_context(request, aiohttp_client, event_loop):
    async def setup_lona_app_context(
            setup_app: Callable[[LonaApp], None],
            project_root: str = '',
    ) -> LonaContext:
        # setup lona app
        lona_app = LonaApp(project_root or str(request.fspath))
        setup_app(lona_app)

        # setup client
        async def setup_aiohttp_app() -> Application:
            lona_app.setup_server(loop=event_loop)

            return cast(Application, lona_app.aiohttp_app)

        client = await aiohttp_client(await setup_aiohttp_app())

        return LonaContext(
            client=client,
            app=lona_app,
            server=cast(LonaServer, lona_app.server),
            event_loop=event_loop,
        )

    return setup_lona_app_context


@pytest.fixture()
def lona_project_context(request, aiohttp_client, event_loop):
    async def setup_lona_project_context(
        project_root: str = '',
        settings: None | list[str] = None,
        settings_pre_overrides: None | dict = None,
        settings_post_overrides: None | dict = None,
    ) -> LonaContext:

        # setup aiohttp app
        server = None

        async def setup_aiohttp_app() -> Application:
            nonlocal server

            # setup lona server
            server = LonaServer(
                project_root=project_root or request.fspath,
                settings_paths=settings or [],
                settings_pre_overrides=settings_pre_overrides or {},
                settings_post_overrides=settings_post_overrides or {},
            )

            server._loop = event_loop
            server._worker_pool = WorkerPool(settings=server.settings)

            return server._app

        client = await aiohttp_client(await setup_aiohttp_app())

        return LonaContext(
            client=client,
            app=None,
            server=cast(LonaServer, server),
            event_loop=event_loop,
        )

    return setup_lona_project_context


def eventually(
        timeout: float = 5,
        interval: float = 1,
) -> Iterator[AsyncContextManager]:

    """
    Wait for expected state in async test.

    The function is meant to be iterated. Each time it returns new attempt.
    Attempt is an async context manager to wrap assertions.
    It suppresses all exceptions until time is out.
    If no exception is raised iteration stops.

    Example::

        counter = 0
        for attempt in eventually():
            async with attempt:
                counter += 1
                assert counter > 3

    :param timeout: time in seconds during which it produces new attempts
    :param interval: seconds to sleep between attempts
    """

    end_time = time.time() + timeout
    success = False

    while not success:
        context_manager_was_used = False

        @asynccontextmanager
        async def attempt() -> AsyncIterator[None]:
            nonlocal context_manager_was_used, success
            context_manager_was_used = True

            try:
                yield  # execute assertions

            except Exception:
                if time.time() > end_time:
                    raise
                else:
                    await sleep(interval)

            else:
                success = True

        yield attempt()

        if not context_manager_was_used:
            raise SyntaxError('context manager must be used')
