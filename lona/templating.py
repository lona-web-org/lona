import builtins
import logging

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger('lona.templating')

BUILTINS = {}

for name in dir(builtins):
    if name.startswith('_'):
        continue

    BUILTINS[name] = getattr(builtins, name)


class Namespace:
    def __init__(self, server):
        self.server = server

    def load_stylesheets(self):
        return self.server.static_file_loader.style_tags_html

    def load_scripts(self):
        return self.server.static_file_loader.script_tags_html

    def _import(self, *args, **kwargs):
        return self.server.acquire(*args, **kwargs)

    def resolve_url(self, *args, **kwargs):
        return self.server.router.reverse(*args, **kwargs)

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

        # resolving potential relative paths
        for index, template_dir in enumerate(self.template_dirs):
            self.template_dirs[index] = self.server.resolve_path(template_dir)

        logger.debug('loading template_dirs %s',
                     repr(self.template_dirs)[1:-1])

        self.jinja2_env = Environment(
            loader=FileSystemLoader(self.template_dirs),
        )

    # public api ##############################################################
    def get_template(self, template_name):
        logger.debug("searching for '%s'", template_name)

        template = self.jinja2_env.get_template(template_name)

        logger.debug("'%s' is '%s' ", template_name, template.filename)

        return template

    def generate_template_context(self, overrides):
        context = {
            'Lona': Namespace(self.server),
            **BUILTINS,
            **self.server.settings.TEMPLATE_EXTRA_CONTEXT,
            **overrides,
        }

        context['_variables'] = context

        return context

    def render_string(self, template_string, template_context={}):
        template = self.jinja2_env.from_string(template_string)

        template_context = self.generate_template_context(
            overrides=template_context)

        return template.render(template_context)

    def render_template(self, template_name, template_context={}):
        template = self.get_template(template_name)

        template_context = self.generate_template_context(
            overrides=template_context)

        return template.render(template_context)
