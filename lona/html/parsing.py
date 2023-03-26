from __future__ import annotations

from html.parser import HTMLParser
from typing import List, Dict
import logging

import html5lib

from lona.compat import get_use_future_node_classes
from lona.html.abstract_node import AbstractNode
from lona.html.nodes.text_content import Div
from lona.html.text_node import TextNode
from lona.html.node import Node

logger = logging.getLogger('lona')


class NodeHTMLParser(HTMLParser):
    CDATA_CONTENT_ELEMENTS = HTMLParser.CDATA_CONTENT_ELEMENTS + ('textarea',)

    NODE_CLASSES: dict[str, type[Node]] = {}
    INPUT_NODE_CLASSES: dict[str, type[Node]] = {}
    FUTURE_NODE_CLASSES: dict[str, type[Node]] = {}  # TODO: remove in 2.0
    SELF_CLOSING_TAGS: list[str] = []

    def __init__(self, *args, use_high_level_nodes=True, node_classes=None,
                 **kwargs):

        self.use_high_level_nodes = use_high_level_nodes
        self.node_classes = node_classes or {}

        # TODO: remove in 2.0
        self.use_future_node_classes = get_use_future_node_classes()

        super().__init__(*args, **kwargs)

    @classmethod
    def _setup_node_classes_cache(cls):
        # this step is necessary to avoid import loops with lona.html

        from lona.html import FUTURE_NODE_CLASSES as _FUTURE_NODE_CLASSES
        from lona.html import INPUT_NODE_CLASSES as _INPUT_NODE_CLASSES
        from lona.html import SELF_CLOSING_TAGS as _SELF_CLOSING_TAGS
        from lona.html import NODE_CLASSES as _NODE_CLASSES

        cls.FUTURE_NODE_CLASSES.update(_FUTURE_NODE_CLASSES)
        cls.INPUT_NODE_CLASSES.update(_INPUT_NODE_CLASSES)
        cls.SELF_CLOSING_TAGS.extend(_SELF_CLOSING_TAGS)
        cls.NODE_CLASSES.update(_NODE_CLASSES)

    def set_current_node(self, node):
        self._node = node

    def get_node_class(self, tag_name, attributes):
        if not self.use_high_level_nodes:
            return Node

        # TODO: remove in 2.0
        if (self.use_future_node_classes and
                tag_name in self.FUTURE_NODE_CLASSES):

            return self.FUTURE_NODE_CLASSES[tag_name]

        # inputs
        if tag_name == 'input':
            input_type = attributes.get('type', 'text')

            if input_type not in self.INPUT_NODE_CLASSES:
                return Node

            return self.INPUT_NODE_CLASSES[input_type]

        # custom node classes
        if tag_name in self.node_classes:
            return self.node_classes[tag_name]

        # nodes from the standard library
        if tag_name in self.NODE_CLASSES:
            return self.NODE_CLASSES[tag_name]

        # generic nodes
        return Node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs, self_closing=True)

    def handle_starttag(self, tag, attrs, self_closing=False):
        self_closing = self_closing or tag in self.SELF_CLOSING_TAGS

        # node attributes
        node_attributes = {}

        for name, value in attrs:
            if value is None:
                value = ''

            if name == 'data-lona-node-id':
                continue

            node_attributes[name] = value

        # tag overrides
        node_kwargs = {}

        node_kwargs['tag_name'] = tag
        node_kwargs['self_closing_tag'] = self_closing

        # setup node
        for key in ('id', 'class', 'style', 'value'):
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


def html5lib_element_to_node(
        html5lib_element,
        use_high_level_nodes=True,
        node_classes=None,
):

    from lona.html import Node, NODE_CLASSES, SELF_CLOSING_TAGS, INPUT_NODE_CLASSES

    # skip comments
    if not isinstance(html5lib_element.tag, str):
        return

    namespace, tag_name = html5lib_element.tag.split('}')

    # find node class
    if use_high_level_nodes:

        # inputs
        if tag_name == 'input':
            input_type = html5lib_element.attrib.get('type', 'text')
            node_class = INPUT_NODE_CLASSES.get(input_type, Node)

        # overrides
        elif node_classes and tag_name in node_classes:
            node_class = node_classes[tag_name]

        else:
            node_class = NODE_CLASSES.get(tag_name, Node)

    else:
        node_class = Node

    # parse namespace
    namespace = namespace[1:]

    if namespace == 'http://www.w3.org/1999/xhtml':
        namespace = None

    # attributes
    node_attributes = {}

    for name, value in html5lib_element.attrib.items():
        if value is None:
            value = ''

        if name == 'data-lona-node-id':
            continue

        # strip namespaces
        if name.startswith('{'):
            name = name.split('}')[1][1:]

        node_attributes[name] = value

    # initialize node
    node = node_class(
        namespace=namespace,
        tag_name=tag_name,
        self_closing_tag=tag_name in SELF_CLOSING_TAGS,
        **node_attributes,
    )

    # child nodes
    if html5lib_element.text:
        text = html5lib_element.text.strip()

        if text:
            node.append(TextNode(text))

    for child_html5lib_element in html5lib_element:
        if child_html5lib_element.text:
            text = child_html5lib_element.text.strip()

            if text:
                node.append(TextNode(text))

        child_node = html5lib_element_to_node(
            html5lib_element=child_html5lib_element,
            use_high_level_nodes=use_high_level_nodes,
            node_classes=node_classes,
        )

        if child_node:
            node.append(child_node)

        if child_html5lib_element.tail:
            tail = child_html5lib_element.tail.strip()

            if tail:
                node.append(TextNode(tail))

    return node


def html_string_to_node_list(html_string, use_high_level_nodes=True,
                             node_classes=None):

    document = html5lib.parse(html_string, treebuilder='lxml')
    body = document.find('//{http://www.w3.org/1999/xhtml}body')
    nodes = []

    for html5lib_element in body:
        child_node = html5lib_element_to_node(
            html5lib_element=html5lib_element,
            use_high_level_nodes=use_high_level_nodes,
            node_classes=node_classes,
        )

        if child_node:
            nodes.append(child_node)

    return nodes


def HTML(
        *nodes: str | AbstractNode,
        use_high_level_nodes: bool = True,
        node_classes: Dict[str, AbstractNode] | None = None,
) -> AbstractNode:

    _nodes: List[AbstractNode] = []

    for node in nodes:

        # strings
        if isinstance(node, str):

            # escaped text
            if node.startswith('\\'):
                _nodes.append(TextNode(node[1:]))

            # html string
            elif '<' in node or '>' in node:
                parsed_nodes = html_string_to_node_list(
                    html_string=node,
                    use_high_level_nodes=use_high_level_nodes,
                    node_classes=node_classes or {},
                )

                if len(nodes) > 1:
                    _nodes.extend(parsed_nodes)

                else:
                    _nodes = parsed_nodes

            else:
                _nodes.append(TextNode(node))

        # lona nodes
        else:
            _nodes.append(node)

    if len(_nodes) == 1:
        return _nodes[0]

    return Div(nodes=_nodes)
