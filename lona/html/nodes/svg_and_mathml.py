from lona.html.node import Node


class SVG(Node):
    NAMESPACE = 'http://www.w3.org/2000/svg'
    TAG_NAME = 'svg'


class MathML(Node):
    TAG_NAME = 'math'
