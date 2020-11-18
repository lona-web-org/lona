import builtins
import logging

from jinja2 import Environment, FileSystemLoader

from lona.utils import acquire

logger = logging.getLogger('lona.templating')

BUILTINS = {}

for name in dir(builtins):
    if name.startswith('_'):
        continue

    BUILTINS[name] = getattr(builtins, name)


class TemplatingEngine:
    # TODO: warn if settings.FRONTEND_TEMPLATE is not available

    def __init__(self, server):
        self.server = server

        self.template_dirs = (self.server.settings.TEMPLATE_DIRS +
                              self.server.settings.CORE_TEMPLATE_DIRS)

        logger.debug('loading template_dirs %s',
                     repr(self.template_dirs)[1:-1])

        self.jinja2_env = Environment(
            loader=FileSystemLoader(self.template_dirs),
        )

    # context functions #######################################################
    def _load_stylesheets(self):
        return self.server.static_file_loader.style_tags_html

    def _load_scripts(self):
        return self.server.static_file_loader.script_tags_html

    def _import(self, *args, **kwargs):
        return acquire(*args, **kwargs)[1]

    def _url(self, *args, **kwargs):
        return self.server.router.reverse(*args, **kwargs)

    # public api ##############################################################
    def get_template(self, template_name):
        logger.debug("searching for '%s'", template_name)

        template = self.jinja2_env.get_template(template_name)

        logger.debug("'%s' is '%s' ", template_name, template.filename)

        return template

    def generate_template_context(self, overrides):
        context = {
            'server': self.server,
            'load_stylesheets': self._load_stylesheets,
            'load_scripts': self._load_scripts,
            'import': self._import,
            'url': self._url,
            **BUILTINS,
            **self.server.settings.TEMPLATE_EXTRA_CONTEXT,
            **overrides,
        }

        context['_variables'] = context

        return context

    def render_template(self, template_name, template_context={}):
        template = self.get_template(template_name)

        template_context = self.generate_template_context(
            overrides=template_context)

        return template.render(template_context)
