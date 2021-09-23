from typing import overload, Optional, Callable, Union, Type, List, Dict, Any
from argparse import RawTextHelpFormatter, ArgumentParser, Namespace
from tempfile import TemporaryDirectory
from asyncio import AbstractEventLoop
from os import PathLike
import contextlib
import logging
import os

from typing_extensions import Literal
from aiohttp.web import Application

from lona.command_line.run_server import run_server
from lona import default_settings, LonaView
from lona.worker_pool import WorkerPool
from lona.logging import setup_logging
from lona.settings import Settings
from lona.server import LonaServer
from lona.routing import Route

logger = logging.getLogger('lona.app')


class LonaApp:
    def __init__(self, script_path: PathLike) -> None:
        self.script_path: PathLike = script_path
        self.project_root: str = os.path.dirname(self.script_path)

        self.aiohttp_app: Optional[Application] = None
        self.server: Optional[LonaServer] = None

        # setup tempdir
        self.temp_dir: TemporaryDirectory = TemporaryDirectory()

        self.template_dir: str = os.path.join(
            self.temp_dir.name,
            'templates',
        )

        self.static_dir: str = os.path.join(
            self.temp_dir.name,
            'static',
        )

        os.makedirs(self.template_dir)
        os.makedirs(self.static_dir)

        # setup routes
        self.routes: List[Route] = []

        # setup settings
        self.settings: Settings = Settings()
        self.settings.add(default_settings.__file__)

    # helper ##################################################################
    def _get_settings_as_dict(self) -> Dict[str, Any]:
        settings = {}

        for name in self.settings:
            settings[name] = self.settings.get(name)

        return settings

    def resolve_path(self, path: str) -> str:
        if path.startswith('/'):
            return path

        return os.path.normpath(
            os.path.join(
                self.project_root,
                path,
            ),
        )

    # decorator ###############################################################
    def route(
            self,
            # 1 = lona.MATCH_ALL  https://github.com/python/mypy/issues/10026
            raw_pattern: Union[str, Literal[1]],
            name: str = '',
            interactive: bool = True,
            http_pass_through: bool = False,
            frontend_view: Union[None, str, LonaView] = None,
    ) -> Callable[[Type[LonaView]], None]:

        def decorator(view_class: Type[LonaView]) -> None:
            self.routes.append(
                Route(
                    raw_pattern=raw_pattern,
                    view=view_class,
                    name=name,
                    interactive=interactive,
                    http_pass_through=http_pass_through,
                    frontend_view=frontend_view,
                ),
            )

        return decorator

    # middleware
    @overload
    def middleware(self) -> Callable[[Type], None]:
        ...

    @overload
    def middleware(self, middleware_class: Type) -> None:
        ...

    def middleware(self, middleware_class: Optional[Type] = None) -> Optional[Callable[[Type], None]]:  # NOQA: LN001
        def decorator(middleware_class: Type) -> None:
            self.settings.MIDDLEWARES.append(middleware_class)

        if callable(middleware_class):
            decorator(middleware_class)

            return None

        else:
            return decorator

    # frontend
    @overload
    def frontend_view(self) -> Callable[[Type[LonaView]], None]:
        ...

    @overload
    def frontend_view(self, view_class: Type[LonaView]) -> None:
        ...

    def frontend_view(self, view_class: Optional[Type[LonaView]] = None) -> Optional[Callable[[Type[LonaView]], None]]:  # NOQA: LN001
        def decorator(view_class: Type[LonaView]) -> None:
            self.settings.FRONTEND_VIEW = view_class

        if callable(view_class):
            decorator(view_class)

            return None

        else:
            return decorator

    # files ###################################################################
    def _add_file(
            self,
            temp_dir: str,
            name: str,
            string: str = '',
            path: str = '',
    ) -> None:

        if name.startswith('/'):
            name = name[1:]

        dirname = os.path.join(
            temp_dir,
            os.path.dirname(name),
        )

        with contextlib.suppress(FileExistsError):
            os.makedirs(dirname)

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
            raise ValueError('either string or path have to be set')

    def add_template(
            self,
            name: str,
            string: str = '',
            path: str = '',
    ) -> None:

        return self._add_file(
            temp_dir=self.template_dir,
            name=name,
            string=string,
            path=path,
        )

    def add_static_file(
            self,
            name: str,
            string: str = '',
            path: str = '',
    ) -> None:

        return self._add_file(
            temp_dir=self.static_dir,
            name=name,
            string=string,
            path=path,
        )

    # command line ############################################################
    def parse_command_line(self) -> Dict:
        from lona.command_line.handle_command_line import (
            parse_overrides,
            DESCRIPTION,
        )

        parser = ArgumentParser(
            prog=str(self.script_path),
            formatter_class=RawTextHelpFormatter,
            description=DESCRIPTION,
        )

        parser.add_argument(
            '-l',
            '--log-level',
            choices=['debug', 'info', 'warn', 'error', 'critical'],
        )

        parser.add_argument(
            '--loggers',
            type=str,
            nargs='+',
        )

        parser.add_argument(
            '--debug-mode',
            choices=['messages', 'views', 'input-events'],
        )

        parser.add_argument(
            '-o',
            '--settings-pre-overrides',
            nargs='+',
        )

        parser.add_argument(
            '-O',
            '--settings-post-overrides',
            nargs='+',
        )

        parser.add_argument(
            '--host',
            type=str,
        )

        parser.add_argument(
            '--port',
            type=int,
        )

        parser.add_argument(
            '--shutdown-timeout',
            type=float,
        )

        parser.add_argument(
            '--shell',
            action='store_true',
        )

        parser.add_argument(
            '--shell-server-url',
            type=str,
        )

        args = vars(parser.parse_args())

        for key, value in args.copy().items():
            if not value:
                args.pop(key)

        if 'settings_pre_overrides' in args:
            args['settings_pre_overrides'] = parse_overrides(
                args['settings_pre_overrides'],
            )

        if 'settings_post_overrides' in args:
            args['settings_post_overrides'] = parse_overrides(
                args['settings_post_overrides'],
            )

        return args

    # server ##################################################################
    def setup_server(
            self,
            loop: Union[AbstractEventLoop, None] = None,
            settings_pre_overrides: Optional[Dict[str, Any]] = None,
            settings_post_overrides: Optional[Dict[str, Any]] = None,
    ) -> None:

        # finish settings
        self.settings.CORE_TEMPLATE_DIRS.insert(0, self.template_dir)
        self.settings.STATIC_DIRS.insert(0, self.static_dir)

        # setup server
        self.aiohttp_app = Application(loop=loop)

        settings_post_overrides = {
            **self._get_settings_as_dict(),
            **(settings_post_overrides or {}),
        }

        self.server = LonaServer(
            app=self.aiohttp_app,
            project_root=self.project_root,
            settings_pre_overrides=settings_pre_overrides,
            settings_post_overrides=settings_post_overrides,
            routes=self.routes,
        )

        # setup worker pool
        worker_pool = WorkerPool(
            settings=self.server.settings,
        )

        self.server.set_loop(loop)
        self.server.set_worker_pool(worker_pool)

    def run(
            self,
            loop: Union[AbstractEventLoop, None] = None,
            parse_command_line: bool = True,
            **args: Any,
    ) -> None:

        # setup arguments
        server_args = Namespace(
            host='localhost',
            port=8080,
            shell_server_url='',
            shutdown_timeout=0,
            log_level='info',
            loggers=[],
            debug_mode='',
            shell=False,
            settings_pre_overrides=None,
            settings_post_overrides=None,
        )

        for key, value in args.items():
            setattr(server_args, key, value)

        if parse_command_line:
            command_line_args = self.parse_command_line()

            for key, value in command_line_args.items():
                setattr(server_args, key, value)

        setup_logging(server_args)

        # setup server
        self.setup_server(
            loop=loop,
            settings_pre_overrides=server_args.settings_pre_overrides,
            settings_post_overrides=server_args.settings_post_overrides,
        )

        # start server
        run_server(
            args=server_args,
            app=self.aiohttp_app,
            server=self.server,
        )
