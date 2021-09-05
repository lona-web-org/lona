import re

from jinja2 import Template
from bs4 import BeautifulSoup

FUNCTION_RE = re.compile(r'\([^)]+\)')

TOC_TREE_TEMPLATE_STRING = """
<ul class="toc-tree">
    {% for section, header, indentation in data %}
        <li>{{ indentation * '&nbsp;&nbsp;&nbsp;&nbsp;' }}<a href="#{{ section .attrs['id'] }}">{{ header }}</a></li>
    {% endfor %}
</ul>
"""  # NOQA

_toc_tree_template = Template(TOC_TREE_TEMPLATE_STRING)


class TocTree:
    def _add_toc_tree(self, content):
        if not content['content_body']:
            return

        if not content.get('toctree', True):
            return

        soup = BeautifulSoup(content['content_body'], 'html.parser')
        toc_tree_data = []

        for section in soup.findAll('div', attrs={'class': 'section'}):
            # find header
            header = None

            for child in section.children:
                if child.name in ('h2', 'h3', 'h4', 'h5', 'h6'):
                    header = child

                    break

            indentation = int(header.name[1:]) - 1

            # add anchor
            anchor = soup.new_tag('a')
            anchor.attrs['class'] = 'anchor'

            anchor.attrs['href'] = f"/{content['output']}#{section.attrs['id']}"

            header.append(anchor)

            # trim header
            header_string = FUNCTION_RE.sub('()', header.text)

            toc_tree_data.append(
                (section, header_string, indentation, )
            )

        # render html with anchors
        if not content['has_anchors']:
            content['content_body'] = str(soup)
            content['has_anchors'] = True

        # render toc tree
        content['toc_tree'] = _toc_tree_template.render(
            data=toc_tree_data,
        )

    def contents_parsed(self, context):
        for content in context.contents:
            self._add_toc_tree(content)

    def render_content(self, context, content):
        self._add_toc_tree(content)
