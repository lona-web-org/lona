from html.parser import HTMLParser
import inspect
import logging

from lona.html.text_node import TextNode
from lona.html.node import Node

logger = logging.getLogger('lona')

NODE_CLASSES = {}
INPUT_NODE_CLASSES = {}

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


def _find_node_classes(module):
    try:
        for attribute_name in dir(module):
            node_class = getattr(module, attribute_name)

            if not inspect.isclass(node_class):
                continue

            if not issubclass(node_class, Node):
                continue

            # input nodes
            if node_class.TAG_NAME == 'input':
                if 'type' not in node_class.ATTRIBUTES:
                    logger.warning(
                        'WARNING: input node %s has no type set',
                        repr(node_class),
                    )

                    continue

                INPUT_NODE_CLASSES[node_class.ATTRIBUTES['type']] = node_class

            # nodes
            else:
                if node_class.TAG_NAME in NODE_CLASSES:
                    logger.warning(
                        'WARNING: Two Node classes with the same tag name were found: %s',  # NOQA
                        node_class.TAG_NAME,
                    )

                NODE_CLASSES[node_class.TAG_NAME] = node_class

    except Exception:
        logger.error(
            'Exception occurred while searching for node classes',
            exc_info=True,
        )


def _setup_node_classes_cache():
    from lona import html

    _find_node_classes(html)


class NodeHTMLParser(HTMLParser):
    def __init__(self, *args, use_high_level_nodes=True, node_classes=None,
                 **kwargs):

        self.use_high_level_nodes = use_high_level_nodes
        self.node_classes = node_classes or {}

        super().__init__(*args, **kwargs)

    def set_current_node(self, node):
        self._node = node

    def get_node_class(self, tag_name, attributes):
        if not self.use_high_level_nodes:
            return Node

        # inputs
        if tag_name == 'input':
            input_type = attributes.get('type', 'text')

            if input_type not in INPUT_NODE_CLASSES:
                return Node

            return INPUT_NODE_CLASSES[input_type]

        # custom node classes
        if tag_name in self.node_classes:
            return self.node_classes[tag_name]

        # nodes from the standard library
        if tag_name in NODE_CLASSES:
            return NODE_CLASSES[tag_name]

        # generic nodes
        return Node

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

        # setup node
        node_class = self.get_node_class(tag, node_kwargs)
        node = node_class(**node_kwargs)

        # setup node
        self._node.append(node)
        self.set_current_node(node)

    def handle_endtag(self, tag):
        self.set_current_node(self._node.parent)

    def handle_data(self, data):
        text = data

        if self._node.tag_name not in ('pre', 'textarea'):
            text = text.strip()

            if not text:
                return

        self._node.append(TextNode(text))


def html_string_to_node_list(html_string, use_high_level_nodes=True,
                             node_classes=None):

    root_node = Node()

    html_parser = NodeHTMLParser(
        use_high_level_nodes=use_high_level_nodes,
        node_classes=node_classes or {},
    )

    html_parser.set_current_node(root_node)
    html_parser.feed(html_string)

    return list(root_node.nodes)
