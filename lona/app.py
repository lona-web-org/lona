from tempfile import TemporaryDirectory
import logging
import os

from lona.command_line.run_server import run_server
from lona.logging import setup_logging
from lona.settings import Settings
from lona.server import LonaServer
from lona import default_settings
from lona.routing import Route

from aiohttp.web import Application

logger = logging.getLogger('lona.app')


class ServerArgs:
    def __init__(self, **args):
        self.add(**args)

    def add(self, **args):
        for key, value in args.items():
            setattr(self, key, value)


class LonaApp:
    def __init__(self, script_path):
        self.script_path = script_path
        self.project_root = os.path.dirname(self.script_path)

        # setup tempdir
        self.temp_dir = TemporaryDirectory()

        self.template_dir = os.path.join(
            self.temp_dir.name,
            'templates',
        )

        self.static_dir = os.path.join(
            self.temp_dir.name,
            'static',
        )

        os.makedirs(self.template_dir)
        os.makedirs(self.static_dir)

        # setup routes
        self.routes = []

        # setup settings
        self.settings = Settings()
        self.settings.add(default_settings.__file__)

    # helper ##################################################################
    def _get_settings_as_dict(self):
        settings = {}

        for name in self.settings:
            settings[name] = self.settings.get(name)

        return settings

    def resolve_path(self, path):
        if path.startswith('/'):
            return path

        return os.path.normpath(
            os.path.join(
                self.project_root,
                path,
            ),
        )

    # decorator ###############################################################
    def route(self, *args, **kwargs):
        def decorator(view_class):
            self.routes.append(
                Route(
                    *args,
                    view=view_class,
                    **kwargs,
                )
            )

        return decorator

    def middleware(self, middleware_class=None):
        def decorator(middleware_class):
            self.settings.MIDDLEWARES.append(middleware_class)

        if callable(middleware_class):
            return decorator(middleware_class)

        else:
            return decorator

        return decorator

    def frontend_view(self, view_class=None):
        def decorator(view_class):
            self.settings.FRONTEND_VIEW = view_class

        if callable(view_class):
            return decorator(view_class)

        else:
            return decorator

        return decorator

    # files ###################################################################
    def _add_file(self, temp_dir, name, string='', path=''):
        if name.startswith('/'):
            name = name[1:]

        dirname = os.path.join(
            temp_dir,
            os.path.dirname(name),
        )

        try:
            os.makedirs(dirname)

        except FileExistsError:
            pass

        full_name = os.path.join(
            dirname,
            os.path.basename(name),
        )

        if path:
            _path = self.resolve_path(path)

            if not os.path.exists(_path):
                raise FileNotFoundError(path)

            os.symlink(os.path.abspath(_path), full_name)

        elif string:
            with open(full_name, 'w+') as f:
                f.write(string)

        else:
            ValueError('either string or path have to be set')

    def add_template(self, name, string='', path=''):
        return self._add_file(
            temp_dir=self.template_dir,
            name=name,
            string=string,
            path=path,
        )

    def add_static_file(self, name, string='', path=''):
        return self._add_file(
            temp_dir=self.static_dir,
            name=name,
            string=string,
            path=path,
        )

    # server ##################################################################
    def run(self, **args):
        # finish settings
        self.settings.CORE_TEMPLATE_DIRS.insert(0, self.template_dir)
        self.settings.STATIC_DIRS.insert(0, self.static_dir)

        # setup arguments
        server_args = ServerArgs(
            host='localhost',
            port=8080,
            shell_server_url='',
            shutdown_timeout=0,
            log_level='info',
            loggers=[],
            debug_mode='',
            shell=False,
        )

        server_args.add(**args)

        # setup logging
        log_formatter, log_filter = setup_logging(server_args)

        # setup server
        app = Application()

        server = LonaServer(
            app=app,
            project_root=self.project_root,
            settings_post_overrides=self._get_settings_as_dict(),
            routes=self.routes,
        )

        # start server
        run_server(
            args=server_args,
            app=app,
            server=server,
        )
