import textwrap
import inspect
import re

from flamingo.plugins.rst import register_directive
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from docutils.parsers.rst import Directive
from pygments import highlight
from docutils.nodes import raw

from lona.imports import acquire

DOC_STRING_ARGUMENT_RE = re.compile(r':[^\s]+:')


class ApiDocDirective(Directive):
    optional_arguments = 1
    has_content = False
    option_spec = {}

    def run(self):
        class_import_string, method_name = self.arguments[0].rsplit('.', 1)
        _class = acquire(class_import_string)
        method = getattr(_class, method_name)
        signature = inspect.signature(method)

        # signature string
        signature_string = f'{self.arguments[0]}('

        for parameter in signature.parameters.values():
            signature_string += f'\n    {str(parameter)},'

        signature_string += '\n)'

        if signature.return_annotation is not inspect._empty:
            signature_string += f' -> {signature.return_annotation}'

        # highlight signature string
        lexer = get_lexer_by_name('python')
        formatter = HtmlFormatter(cssclass='highlight signature')

        signature_string = highlight(signature_string, lexer, formatter)

        # docstring
        doc_string = textwrap.indent(
            textwrap.dedent(method.__doc__),
            prefix='    ',
        )

        def insert_strongs(match):
            span = match.span()

            return f'<strong>{match.string[span[0]:span[1]]}</strong>'

        doc_string = DOC_STRING_ARGUMENT_RE.sub(
            insert_strongs,
            doc_string,
        )

        # return raw HTML
        return [
            raw(
                '',
                f'<div class="api-doc">{signature_string}<pre class="doc-string">{doc_string}</pre></div>',
                format='html',
            ),
        ]


class ApiDoc:
    def parser_setup(self, context):
        register_directive('api-doc', ApiDocDirective)
