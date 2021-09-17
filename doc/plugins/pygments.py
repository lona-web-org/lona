# source: https://github.com/pengutronix/flamingo/blob/master/flamingo/plugins/rst/pygments.py  # NOQA: E501

from tempfile import TemporaryDirectory
import os

from pygments.styles import get_style_by_name, get_all_styles
from pygments.lexers import get_lexer_by_name, guess_lexer
from docutils.parsers.rst import directives, Directive
from flamingo.plugins.rst import register_directive
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from pygments.token import Token
from pygments import highlight
from docutils.nodes import raw


def code_block(context):
    class CodeBlock(Directive):
        optional_arguments = 1
        has_content = True

        option_spec = {
            'license': directives.unchanged,
            'template': directives.unchanged,
            'include': directives.unchanged,
        }

        def run(self):
            content = ''

            if self.content:
                content += '\n'.join(self.content)

            if 'include' in self.options:
                if content:
                    content += '\n'

                path = os.path.join(
                    context.settings.CONTENT_ROOT,
                    os.path.dirname(context.content['path']),
                    self.options['include'],
                )

                content += open(path, 'r').read()

            try:
                if self.arguments:
                    lexer = get_lexer_by_name(self.arguments[0])

                else:
                    lexer = guess_lexer(content)

            except (ClassNotFound, IndexError):
                lexer = get_lexer_by_name('text')

            formatter = HtmlFormatter()
            content = highlight(content, lexer, formatter)

            # find template
            template = self.options.get(
                'template', context.settings.DEFAULT_CODE_BLOCK_TEMPLATE)

            node_content = context.templating_engine.render(
                template,
                {
                    'context': context,
                    'content': content,
                    'license': self.options.get('license', ''),
                },
                handle_exceptions=False,
            )

            return [
                raw('', node_content, format='html')
            ]

    return CodeBlock


class rstPygments:
    def get_options(self):
        options = [
            ('theme', [(i, i == self.theme_name, )
                       for i in get_all_styles()], ),

            ('background color', self.style.background_color, ),
        ]

        styles = []

        for key, value in self.style.styles.items():
            styles.append(
                (str(key), str(value), ),
            )

        styles = sorted(styles, key=lambda v: v[0])

        return options + styles

    def reset_options(self):
        self.theme_name = self.context.settings.get(
            'PYGMENTS_THEME',
            'default',
        )

        self.background_color = self.context.settings.get(
            'PYGMENTS_BACKGROUND_COLOR',
            '',
        )

        self.overrides = self.context.settings.get(
            'PYGMENTS_OVERRIDES',
            {},
        )

        self.build()

    def set_option(self, name, value):
        if name == 'theme':
            self.theme_name = value
            self.backgroung_color = ''
            self.overrides = {}

        elif name == 'background color':
            self.background_color = value

        else:
            token = Token

            for attr_name in name.split('.')[1:]:
                token = getattr(token, attr_name)

            self.overrides[token] = value

        self.build()

    def build(self):
        parent_class = get_style_by_name(self.theme_name)

        class Style(parent_class):
            default_style = ''

            background_color = (self.background_color or
                                parent_class.background_color)

            styles = {
                **parent_class.styles,
                **self.overrides
            }

        self.style = Style
        formatter = HtmlFormatter(style=Style)

        html = formatter.get_style_defs(
            self.context.settings.get('PYGMENTS_CSS_SELECTOR', '.highlight'))

        with open(self.path, 'w+') as f:
            f.write(html)

    def settings_setup(self, context):
        self.context = context

        # setup pygments build directory
        self.temp_dir = TemporaryDirectory()
        self.theme_path = os.path.join(self.temp_dir.name, 'pygments/theme/')
        self.path = os.path.join(self.theme_path, 'static/pygments.css')

        self.context.mkdir_p(self.path, force=True)

        # compile pygments
        self.reset_options()

        # register flamingo theme
        self.THEME_PATHS = [
            self.theme_path,
        ]

        context.settings.LIVE_SERVER_IGNORE_PREFIX.append(self.temp_dir.name)

    def parser_setup(self, context):
        register_directive('code-block', code_block(context))
