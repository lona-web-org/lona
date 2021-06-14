# source: https://github.com/pengutronix/flamingo/blob/master/doc/plugins/rst_setting.py

from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments import highlight

from flamingo.core.utils.imports import acquire
from flamingo.core.utils.pprint import pformat
from flamingo.plugins.rst import parse_rst

RAW_SETTING_TEMPLATE = """
<div class="raw-setting">
    {highlight}
    <div class="description">
        {description}
    </div>
</div>
"""

SETTING_TEMPLATE = """
<div class="setting">
    <div class="highlight">
        <pre>{name} = </pre><pre>{value}</pre>
    </div>
</div>
<div class="clearfix"></div>
<div class="setting-description">{description}</div>
"""


class RawHtmlFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        for i, t in source:
            yield i, t


def raw_setting(context):
    class RawSetting(Directive):
        optional_arguments = 0
        has_content = True

        def run(self):
            python, description = (
                '\n'.join(self.content).split('\n\n', 1) + [''])[0:2]

            lexer = get_lexer_by_name('python')
            formatter = HtmlFormatter()
            html = highlight(python, lexer, formatter)

            return [
                raw(
                    '',
                    RAW_SETTING_TEMPLATE.format(
                        highlight=html,
                        description=parse_rst(description, context),
                    ),
                    format='html',
                )
            ]

    return RawSetting


def setting(context):
    class Setting(Directive):
        optional_arguments = 0
        has_content = True

        option_spec = {
            'name': directives.unchanged,
            'path': directives.unchanged,
        }

        def run(self):
            if 'name' not in self.options or 'path' not in self.options:
                context.logger.error(
                    "%s: setting: 'name' and 'path' are required",
                    context.content['path'],
                )

                return []

            try:
                value = acquire(self.options['path'])[0]

            except AttributeError:
                context.logger.error(
                    '%s: unable to import %s',
                    context.content['path'],
                    self.options['path']
                )

                return []

            lexer = get_lexer_by_name('python')
            formatter = RawHtmlFormatter()
            html = highlight(pformat(value), lexer, formatter)

            return [
                raw(
                    '',
                    SETTING_TEMPLATE.format(
                        name=self.options['name'],
                        value=html,
                        description=parse_rst(self.content, context)
                    ),
                    format='html',
                )
            ]

    return Setting


class rstSetting:
    def parser_setup(self, context):
        directives.register_directive('raw-setting', raw_setting(context))
        directives.register_directive('setting', setting(context))
