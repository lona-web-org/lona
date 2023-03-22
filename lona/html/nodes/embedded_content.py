from lona.html.node import Node


class Embed(Node):
    TAG_NAME = 'embed'
    SELF_CLOSING_TAG = True


class IFrame(Node):
    TAG_NAME = 'iframe'


class Object(Node):
    TAG_NAME = 'object'


class Picture(Node):
    TAG_NAME = 'picture'


class Portal(Node):
    TAG_NAME = 'portal'


class Source(Node):
    TAG_NAME = 'source'
    SELF_CLOSING_TAG = True
