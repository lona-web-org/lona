from lona.html.node import Node


class Caption(Node):
    TAG_NAME = 'caption'


class Col(Node):
    TAG_NAME = 'col'
    SELF_CLOSING_TAG = True


class ColGroup(Node):
    TAG_NAME = 'colgroup'


class Table(Node):
    TAG_NAME = 'table'


class TBody(Node):
    TAG_NAME = 'tbody'


class Td(Node):
    TAG_NAME = 'td'


class TFoot(Node):
    TAG_NAME = 'tfoot'


class Th(Node):
    TAG_NAME = 'th'


class THead(Node):
    TAG_NAME = 'thead'


class Tr(Node):
    TAG_NAME = 'tr'
