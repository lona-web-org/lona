import logging

from jinja2 import Environment, FileSystemLoader


logger = logging.getLogger('lona.templating')


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

    def get_template(self, template_name):
        logger.debug("searching for '%s'", template_name)

        template = self.jinja2_env.get_template(template_name)

        logger.debug("'%s' is '%s' ", template_name, template.filename)

        return template

    def generate_template_context(self):
        # TODO: get standard template context from settings

        return {}

    def render_template(self, template_name, template_context={}):
        template = self.get_template(template_name)

        template_context = {
            **self.generate_template_context(),
            **template_context,
        }

        return template.render(template_context)
