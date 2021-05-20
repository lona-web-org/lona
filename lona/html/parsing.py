from html.parser import HTMLParser

from lona.html.text_node import TextNode
from lona.html.node import Node

SELF_CLOSING_TAGS = [
    'area',
    'base',
    'br',
    'col',
    'embed',
    'hr',
    'img',
    'input',
    'link',
    'meta',
    'param',
    'source',
    'track',
    'wbr',
]


class NodeHTMLParser(HTMLParser):
    def set_current_node(self, node):
        self._node = node

    def handle_starttag(self, tag, attrs):
        node_kwargs = {}

        # node attributes
        for name, value in attrs:
            if value is None:
                value = 'true'

            node_kwargs[name] = value

        # tag overrides
        node_kwargs['tag_name'] = tag
        node_kwargs['self_closing_tag'] = tag in SELF_CLOSING_TAGS

        node = Node(**node_kwargs)
        self._node.append(node)
        self.set_current_node(node)

    def handle_endtag(self, tag):
        self.set_current_node(self._node.parent)

    def handle_data(self, data):
        self._node.append(TextNode(data))


def html_string_to_node_list(html_string):
    root_node = Node()
    html_parser = NodeHTMLParser()

    html_parser.set_current_node(root_node)
    html_parser.feed(html_string)

    return list(root_node.nodes)
