from __future__ import annotations

from tempfile import TemporaryDirectory
from typing import Dict, Any
import logging
import os

from jinja2 import FileSystemLoader, Environment

from lona.protocol import ENUMS
from lona._json import dumps

SOURCE_ROOT = os.path.join(os.path.dirname(__file__), 'client')

SOURCE_FILES = [
    '_lona/window-shim.js',
    '_lona/dom-renderer.js',
    '_lona/dom-updater.js',
    '_lona/widget-data-updater.js',
    '_lona/input-events.js',
    '_lona/window.js',
    '_lona/context.js',
]

logger = logging.getLogger('lona.client_pre_compiler')


class ClientPreCompiler:
    def __init__(self, server):
        self.server = server

        # setup temp dir
        self.tmp_dir = TemporaryDirectory()

        os.makedirs(os.path.join(self.tmp_dir.name, '_lona'))

        # setup templating environment
        self.jinja2_env = Environment(
            loader=FileSystemLoader(SOURCE_ROOT),
        )

        # compile
        if self.server.settings.CLIENT_DEBUG:
            logger.warning('running in debug mode')

        self.compile()

    def get_settings(self) -> Dict[str, Any]:
        settings = self.server.settings

        return {
            'DEBUG': settings.CLIENT_DEBUG,
            'VIEW_START_TIMEOUT': settings.CLIENT_VIEW_START_TIMEOUT,
            'INPUT_EVENT_TIMEOUT': settings.CLIENT_INPUT_EVENT_TIMEOUT,
            'PING_INTERVAL': settings.CLIENT_PING_INTERVAL,
        }

    def get_enums(self) -> Dict[str, Dict[str, Any]]:
        enums = {}

        for enum in ENUMS:
            enum_values = {}

            for enum_value in enum:
                enum_values[enum_value.name] = enum_value.value

            enums[enum.__name__] = enum_values

        return enums

    def get_source_files(self) -> list[str]:
        if self.server.settings.CLIENT_DEBUG:
            return [
                '_lona/lona.js',
                *SOURCE_FILES,
            ]

        return [
            '_lona/lona.js',
        ]

    def compile(self) -> None:
        logger.debug('pre compiling client')

        if self.server.settings.CLIENT_DEBUG:
            logger.debug('running in debug mode')

        for source_file in self.get_source_files():
            logger.debug('pre compiling %s', source_file)

            try:
                template = self.jinja2_env.get_template(source_file)

                template_context = {
                    'DEBUG': self.server.settings.CLIENT_DEBUG,
                    'source_files': SOURCE_FILES,
                    'protocol': dumps(self.get_enums()),
                    'settings': dumps(self.get_settings()),
                }

                file_content = template.render(
                    **template_context,
                )

                path = os.path.join(
                    self.tmp_dir.name,
                    source_file,
                )

                with open(path, 'w+') as f:
                    f.write(file_content)

            except Exception:  # pragma: no cover
                logger.exception(
                    'exception raised while pre compiling %s',
                    source_file,
                )

    def resolve_path(self, path: str) -> str:
        full_path = os.path.join(self.tmp_dir.name, path)

        if not os.path.exists(full_path):
            return ''

        if self.server.settings.CLIENT_DEBUG:
            self.compile()

        return full_path

    def __repr__(self):
        return f'<ClientPreCompiler({self.path})>'  # pragma: no cover
