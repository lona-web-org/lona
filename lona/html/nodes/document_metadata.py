from lona.html.node import Node


class Base(Node):
    TAG_NAME = 'base'
    SELF_CLOSING_TAG = True


class Head(Node):
    TAG_NAME = 'head'


class Link(Node):
    TAG_NAME = 'link'
    SELF_CLOSING_TAG = True


class Meta(Node):
    TAG_NAME = 'meta'
    SELF_CLOSING_TAG = True


class Style(Node):
    TAG_NAME = 'style'


class Title(Node):
    TAG_NAME = 'title'
