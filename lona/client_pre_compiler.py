from tempfile import TemporaryDirectory
import logging
import os

from jinja2 import Environment, FileSystemLoader

from lona.types import Symbol
from lona.json import dumps

SOURCE_ROOT = os.path.join(os.path.dirname(__file__), 'client')

logger = logging.getLogger('lona.client_pre_compiler')


class ClientPreCompiler:
    def __init__(self, server):
        self.server = server

        self.tmp_dir = TemporaryDirectory()

        self.jinja2_env = Environment(
            loader=FileSystemLoader(SOURCE_ROOT),
        )

        self.compile()

    def _get_path(self):
        return os.path.join(self.tmp_dir.name, 'lona.js')

    def get_settings(self):
        settings = self.server.settings

        return {
            'VIEW_START_TIMEOUT': settings.CLIENT_VIEW_START_TIMEOUT,
            'INPUT_EVENT_TIMEOUT': settings.CLIENT_INPUT_EVENT_TIMEOUT,
        }

    def compile(self):
        logger.debug('pre compiling client')

        try:
            path = self._get_path()
            template = self.jinja2_env.get_template('lona.js')

            template_context = {
                'symbols': dumps(Symbol.dump_symbol_classes()),
                'settings': dumps(self.get_settings()),
            }

            file_content = template.render(
                **template_context,
            )

            with open(path, 'w+') as f:
                f.write(file_content)
                f.close()

        except Exception:
            logger.error(
                'exception raised while pre compiling js client',
                exc_info=True,
            )

    def resolve(self):
        if self.server.settings.CLIENT_RECOMPILE:
            self.compile()

        return self._get_path()

    def __repr__(self):
        return '<ClientPreCompiler({})>'.format(self._get_path())
