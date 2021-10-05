from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Callable
from typing import AsyncContextManager, cast
from asyncio import AbstractEventLoop, sleep
from contextlib import asynccontextmanager
from dataclasses import dataclass
import time

from aiohttp.test_utils import TestClient
from aiohttp.web import Application
import pytest

from lona.worker_pool import WorkerPool
from lona.server import LonaServer
from lona import LonaApp


@dataclass
class LonaContext:
    client: TestClient
    app: None | LonaApp
    server: LonaServer

    def make_url(self, path: str = '') -> str:
        return str(self.client.make_url(path))


@pytest.fixture()
def lona_app_context(request, aiohttp_client):
    async def setup_lona_app_context(
            setup_app: Callable[[LonaApp], None],
            project_root: str = '',
    ) -> LonaContext:
        # setup lona app
        lona_app = LonaApp(project_root or str(request.fspath))
        setup_app(lona_app)

        # setup client
        def setup_aiohttp_app(loop: AbstractEventLoop) -> Application:
            lona_app.setup_server(loop=loop)

            return cast(Application, lona_app.aiohttp_app)

        client = await aiohttp_client(setup_aiohttp_app)

        return LonaContext(
            client=client,
            app=lona_app,
            server=cast(LonaServer, lona_app.server),
        )

    return setup_lona_app_context


@pytest.fixture()
def lona_project_context(request, aiohttp_client):
    async def setup_lona_project_context(
        project_root: str = '',
        settings: None | list[str] = None,
        settings_pre_overrides: None | dict = None,
        settings_post_overrides: None | dict = None,
    ) -> LonaContext:

        # setup aiohttp app
        server = None

        def setup_aiohttp_app(loop: AbstractEventLoop) -> Application:
            nonlocal server

            aiohttp_app = Application(loop=loop)

            # setup lona server
            server = LonaServer(
                app=aiohttp_app,
                project_root=project_root or request.fspath,
                settings_paths=settings or [],
                settings_pre_overrides=settings_pre_overrides or {},
                settings_post_overrides=settings_post_overrides or {},
            )

            server.set_loop(loop)
            server.set_worker_pool(WorkerPool(settings=server.settings))

            return aiohttp_app

        client = await aiohttp_client(setup_aiohttp_app)

        return LonaContext(
            client=client,
            app=None,
            server=cast(LonaServer, server),
        )

    return setup_lona_project_context


def eventually(timeout: float = 5, interval: float = 1) -> Iterator[AsyncContextManager]:  # NOQA: LN001
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
