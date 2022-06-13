import builtins
import logging
import json
import os

from jinja2 import FileSystemLoader, Environment

from lona.protocol import get_enum_values

logger = logging.getLogger('lona.templating')

BUILTINS = {}

for name in dir(builtins):
    if name.startswith('_'):
        continue

    BUILTINS[name] = getattr(builtins, name)


class Namespace:
    def __init__(self, server, templating_engine):
        self.server = server
        self.templating_engine = templating_engine

    @property
    def reverse(self):
        return self.server.reverse

    @property
    def settings(self):
        return self.server.settings

    @property
    def state(self):
        return self.server.state

    def load_stylesheets(self):
        return self.server._static_file_loader.style_tags_html

    def load_scripts(self):
        return self.server._static_file_loader.script_tags_html

    def _import(self, *args, **kwargs):
        return self.server.acquire(*args, **kwargs)

    def load_static_file(self, path):
        logger.debug('resolving static file path %s', path)

        if path.startswith('/'):
            path = path[1:]

        if path in self.templating_engine.static_path_cache:
            logger.debug('%s is cached', path)

        else:
            resolved_path = self.server._static_file_loader.resolve_path(path)

            if not resolved_path:
                logger.error("static file '%s' was not found", path)

                return ''

            self.templating_engine.static_path_cache.append(path)

        return os.path.join(
            self.server.settings.STATIC_URL_PREFIX,
            path,
        )

    def get_protocol_as_json(self):
        return json.dumps(get_enum_values())

    def get_settings_as_json(self):
        settings = {
            'DEBUG': self.settings.CLIENT_DEBUG,
            'VIEW_START_TIMEOUT': self.settings.CLIENT_VIEW_START_TIMEOUT,
            'INPUT_EVENT_TIMEOUT': self.settings.CLIENT_INPUT_EVENT_TIMEOUT,
            'PING_INTERVAL': self.settings.CLIENT_PING_INTERVAL,
        }

        return json.dumps(settings)

    def __getattribute__(self, name):
        # this is necessary because in python its illegal to name a
        # function 'import'

        if name == 'import':
            return super().__getattribute__('_import')

        return super().__getattribute__(name)


class TemplatingEngine:
    def __init__(self, server):
        self.server = server

        self.template_dirs = (self.server.settings.TEMPLATE_DIRS +
                              self.server.settings.CORE_TEMPLATE_DIRS)

        self.static_path_cache = []

        # resolving potential relative paths
        for index, template_dir in enumerate(self.template_dirs):
            self.template_dirs[index] = self.server.resolve_path(template_dir)

        logger.debug('loading template_dirs %s',
                     repr(self.template_dirs)[1:-1])

        self.jinja2_env = Environment(
            loader=FileSystemLoader(
                self.template_dirs,
                followlinks=True,
            ),
        )

        # load extra filters
        logger.debug(
            'loading extra filters from settings.TEMPLATE_EXTRA_FILTERS',
        )

        for name, func in self.server.settings.TEMPLATE_EXTRA_FILTERS.items():
            self.jinja2_env.filters[name] = func

    # public api ##############################################################
    def get_template(self, template_name):
        logger.debug("searching for '%s'", template_name)

        template = self.jinja2_env.get_template(template_name)

        logger.debug("'%s' is '%s' ", template_name, template.filename)

        return template

    def generate_template_context(self, overrides):
        context = {
            'Lona': Namespace(
                server=self.server,
                templating_engine=self,
            ),
            **BUILTINS,
            **self.server.settings.TEMPLATE_EXTRA_CONTEXT,
            **overrides,
        }

        context['_variables'] = context

        return context

    def render_string(self, template_string, template_context=None):
        template = self.jinja2_env.from_string(template_string)

        template_context = self.generate_template_context(
            overrides=template_context or {})

        return template.render(template_context)

    def render_template(self, template_name, template_context=None):
        template = self.get_template(template_name)

        template_context = self.generate_template_context(
            overrides=template_context or {})

        return template.render(template_context)
