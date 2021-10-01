from __future__ import annotations

from html.parser import HTMLParser
import logging
import inspect

from lona.html.text_node import TextNode
from lona.html.node import Node

logger = logging.getLogger('lona')

NODE_CLASSES: dict[str, type[Node]] = {}
INPUT_NODE_CLASSES: dict[str, type[Node]] = {}

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
                        'WARNING: input node %r has no type set',
                        node_class,
                    )

                    continue

                if node_class.ATTRIBUTES['type'] in INPUT_NODE_CLASSES:
                    logger.warning(
                        "WARNING: Two input Node classes with type '%s' were found: %r and %r",
                        node_class.ATTRIBUTES['type'],
                        INPUT_NODE_CLASSES[node_class.ATTRIBUTES['type']],
                        node_class,
                    )

                INPUT_NODE_CLASSES[node_class.ATTRIBUTES['type']] = node_class

            # nodes
            else:
                if node_class.TAG_NAME in NODE_CLASSES:
                    logger.warning(
                        "WARNING: Two Node classes with tag name '%s' were found: %r and %r",
                        node_class.TAG_NAME,
                        NODE_CLASSES[node_class.TAG_NAME],
                        node_class,
                    )

                NODE_CLASSES[node_class.TAG_NAME] = node_class

    except Exception:
        logger.exception('Exception occurred while searching for node classes')


def _setup_node_classes_cache():
    from lona import html

    _find_node_classes(html)


class NodeHTMLParser(HTMLParser):
    CDATA_CONTENT_ELEMENTS = HTMLParser.CDATA_CONTENT_ELEMENTS + ('textarea',)

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

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs, self_closing=True)

    def handle_starttag(self, tag, attrs, self_closing=False):
        self_closing = self_closing or tag in SELF_CLOSING_TAGS

        # node attributes
        node_attributes = {}

        for name, value in attrs:
            if value is None:
                value = ''

            node_attributes[name] = value

        # tag overrides
        node_kwargs = {}

        node_kwargs['tag_name'] = tag
        node_kwargs['self_closing_tag'] = self_closing

        # setup node
        for key in ('id', 'class', 'style'):
            if key in node_attributes:
                node_kwargs[key] = node_attributes.pop(key)

        node_class = self.get_node_class(tag, node_attributes)
        node = node_class(**node_kwargs)

        # set attributes
        node.attributes.update(node_attributes)

        # setup node
        self._node.append(node)
        if not self_closing:
            self.set_current_node(node)

    def handle_data(self, data):
        text = data

        if self._node.tag_name not in ('pre', 'textarea'):
            text = text.strip()

            if not text:
                return

        # textareas
        if self._node.tag_name == 'textarea':
            self._node.value = data

        # normal nodes
        else:
            self._node.append(TextNode(text))

    def handle_endtag(self, tag):
        if self._node.parent is None:
            raise ValueError(
                f'Invalid html: missing start tag for </{tag}>',
            )
        if tag != self._node.tag_name:
            raise ValueError(
                f'Invalid html: </{self._node.tag_name}> expected, </{tag}> received',
            )

        self.set_current_node(self._node.parent)


def html_string_to_node_list(html_string, use_high_level_nodes=True,
                             node_classes=None):

    root_node = Node()

    html_parser = NodeHTMLParser(
        use_high_level_nodes=use_high_level_nodes,
        node_classes=node_classes or {},
    )

    html_parser.set_current_node(root_node)
    html_parser.feed(html_string)

    if html_parser._node is not root_node:
        raise ValueError(
            f'Invalid html: missing end tag </{html_parser._node.tag_name}>',
        )

    return list(root_node.nodes)
