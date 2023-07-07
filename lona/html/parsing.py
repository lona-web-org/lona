from __future__ import annotations

from html.parser import (  # type: ignore[attr-defined]
    attrfind_tolerant,
    tagfind_tolerant,
    HTMLParser,
)
from typing import List, Dict, cast
from html import unescape
import logging

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

    # this method is taken from
    # https://github.com/python/cpython/blob/v3.11.2/Lib/html/parser.py#L300
    def parse_starttag(self, i):
        self.__starttag_text = None
        endpos = self.check_for_whole_start_tag(i)
        if endpos < 0:
            return endpos
        rawdata = self.rawdata
        self.__starttag_text = rawdata[i:endpos]

        # Now parse the data between i+1 and j into a tag and attrs
        attrs = []
        match = tagfind_tolerant.match(rawdata, i+1)
        assert match, 'unexpected call to parse_starttag()'
        k = match.end()
        self.lasttag = tag = match.group(1).lower()
        while k < endpos:
            m = attrfind_tolerant.match(rawdata, k)
            if not m:
                break
            attrname, rest, attrvalue = m.group(1, 2, 3)
            if not rest:
                attrvalue = None
            elif attrvalue[:1] == '\'' == attrvalue[-1:] or \
                 attrvalue[:1] == '"' == attrvalue[-1:]:  # NOQA: Q003,E127
                attrvalue = attrvalue[1:-1]
            if attrvalue:
                attrvalue = unescape(attrvalue)
            attrs.append((attrname, attrvalue))
            k = m.end()

        end = rawdata[k:endpos].strip()
        if end not in (">", "/>"):  # NOQA: Q000
            self.handle_data(rawdata[i:endpos])
            return endpos
        if end.endswith('/>'):
            # XHTML-style empty tag: <span attr="value" />
            self.handle_startendtag(tag, attrs)
        else:
            self.handle_starttag(tag, attrs)
            if tag in self.CDATA_CONTENT_ELEMENTS:
                self.set_cdata_mode(tag)
        return endpos

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


def parse_html(
        html_string: str,
        use_high_level_nodes: bool = True,
        node_classes: Dict[str, AbstractNode] | None = None,
        flat: bool = True,
) -> AbstractNode | List[AbstractNode]:

    """
    Takes HTML as a string and returns a Lona HTML node or a list of Lona
    HTML nodes.

    :use_high_level_nodes:  When set to True, node classes from the standard
                            library get used. When set to False,
                            `lona.html.Node` will be used for all returned
                            nodes.

    :node_classes:          A dict that contains node classes that should be
                            used for the returned HTML nodes.

    :flat:                  If set to True and the parsed HTML tree has exactly
                            one root node, this root node gets returned instead
                            of a list of one node.

    """

    root_node: Node = Node()
    nodes: List[AbstractNode] = []

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

    for node in list(root_node.nodes):
        node.remove()
        nodes.append(node)

    if flat and len(nodes) == 1:
        return nodes[0]

    return nodes


def HTML(
        *nodes: str | AbstractNode,
        use_high_level_nodes: bool = True,
        node_classes: Dict[str, AbstractNode] | None = None,
) -> AbstractNode:

    # TODO: remove HTML parsing in 2.0

    _nodes: List[AbstractNode] = []

    for node in nodes:

        # strings
        if isinstance(node, str):

            # escaped text
            if node.startswith('\\'):
                _nodes.append(TextNode(node[1:]))

            # html string
            elif '<' in node or '>' in node:
                parsed_nodes = cast(
                    list,
                    parse_html(
                        html_string=node,
                        use_high_level_nodes=use_high_level_nodes,
                        node_classes=node_classes or {},
                        flat=False,
                    ),
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
