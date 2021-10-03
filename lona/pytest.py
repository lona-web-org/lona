from __future__ import annotations

from asyncio import AbstractEventLoop
from dataclasses import dataclass
from collections import Callable
from typing import cast

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
