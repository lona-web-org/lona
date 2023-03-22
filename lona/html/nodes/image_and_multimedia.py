from lona.html.node import Node


class Area(Node):
    TAG_NAME = 'area'
    SELF_CLOSING_TAG = True


class Audio(Node):
    TAG_NAME = 'audio'


class Img(Node):
    TAG_NAME = 'img'
    SELF_CLOSING_TAG = True


class Map(Node):
    TAG_NAME = 'map'


class Track(Node):
    TAG_NAME = 'track'
    SELF_CLOSING_TAG = True


class Video(Node):
    TAG_NAME = 'video'
