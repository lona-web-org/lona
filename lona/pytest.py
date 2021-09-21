from aiohttp.web import Application
import pytest

from lona.worker_pool import WorkerPool
from lona.server import LonaServer
from lona import LonaApp


class LonaContext:
    def __init__(self, client, app, server):
        self.client = client
        self.app = app
        self.server = server

    def make_url(self, path=''):
        return str(self.client.make_url(path))


@pytest.fixture()
def lona_app_context(request, aiohttp_client):
    async def setup_lona_app_context(setup_app, project_root=''):
        # setup lona app
        lona_app = LonaApp(project_root or request.fspath)
        setup_app(lona_app)

        # setup client
        def setup_aiohttp_app(loop):
            lona_app.setup_server(loop=loop)

            return lona_app.aiohttp_app

        client = await aiohttp_client(setup_aiohttp_app)

        return LonaContext(
            client=client,
            app=lona_app,
            server=lona_app.server,
        )

    return setup_lona_app_context


@pytest.fixture()
def lona_project_context(request, aiohttp_client):
    async def setup_lona_project_context(
        project_root='',
        settings=None,
        settings_pre_overrides=None,
        settings_post_overrides=None,
    ):

        # setup aiohttp app
        server = None

        def setup_aiohttp_app(loop):
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
            server=server,
        )

    return setup_lona_project_context
