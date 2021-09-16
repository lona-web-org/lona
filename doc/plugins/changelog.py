from docutils.parsers.rst import Directive
from docutils.nodes import raw

from flamingo.plugins.rst import register_directive

GITHUB_RELEASES_BASE_URL = 'https://github.com/lona-web-org/lona/releases/tag/'


class ChanglogHeader(Directive):
    required_arguments = 2
    has_content = False

    def run(self):
        release_name = self.arguments[0]
        date_string = self.arguments[1]

        return [
            raw(
                '',
                f"""
                    <h2 id="{release_name}">
                        <a href="{GITHUB_RELEASES_BASE_URL}/{release_name}">{release_name}</a>
                        {date_string}
                        <a class="anchor" href="/changelog.html#{release_name}"></a>
                    </h2>
                """,  # NOQA: E501
                format='html',
            ),
        ]


class Changelog:
    def parser_setup(self, context):
        register_directive('changelog-header', ChanglogHeader)
