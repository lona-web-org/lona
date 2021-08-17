from lona.static_files import Script
from lona.html.widget import Widget
from lona.html.node import Node


class CanvasNode(Node):
    TAG_NAME = 'canvas'


class CanvasContext:
    def __init__(self, widget):
        self._widget = widget

    def _gen_callback(self, name):
        def callback(*args):
            self._widget.data['operations'].append(
                ['call', name, list(args)],
            )

        return callback

    def __getattribute__(self, name):
        if name.startswith('_'):
            return super().__getattribute__(name)

        return self._gen_callback(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super().__setattr__(name, value)

        self._widget.data['operations'].append(
            ['set', name, value],
        )


class Canvas(Widget):
    FRONTEND_WIDGET_CLASS = 'LonaCanvasWidget'

    STATIC_FILES = [
        Script(name='LonaCanvasWidget', path='canvas.js'),
    ]

    def __init__(self, *args, **kwargs):
        self.nodes = [
            CanvasNode(*args, **kwargs),
        ]

        self.data = {
            'context': '2d',
            'operations': [],
        }

        self.ctx = CanvasContext(widget=self)
