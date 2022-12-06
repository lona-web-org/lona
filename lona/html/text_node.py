from lona.html.abstract_node import AbstractNode
from lona.protocol import NODE_TYPE


class TextNode(AbstractNode):
    def __init__(self, string):
        self._string = str(string)

    def wrap_method(self, method):
        def wrapper(*args, **kwargs):
            return_value = method(*args, **kwargs)

            if isinstance(return_value, str):
                return TextNode(return_value)

            return return_value

        return wrapper

    def __getattribute__(self, name):
        if name in ('id', '_string'):
            return super().__getattribute__(name)

        if hasattr(self, '_string') and hasattr(self._string, name):
            attribute = getattr(self._string, name)

            if callable(attribute):
                return self.wrap_method(attribute)

        return super().__getattribute__(name)

    def __dir__(self):
        return dir(self._string)

    def __add__(self, other):
        string = other

        if isinstance(string, TextNode):
            string = string._string

        return TextNode(self._string + string)

    def __getitem__(self, key):
        return TextNode(self._string[key])

    def __iadd__(self, other):
        raise TypeError('unsupported operation: +=')

    def __str__(self):
        return self._string

    def __len__(self):
        return len(self._string)

    def __bool__(self):
        return True

    def __repr__(self):
        return f'<TextNode({self._string!r})>'

    # serialization ###########################################################
    def _serialize(self, include_node_ids=True):
        data = [NODE_TYPE.TEXT_NODE, self.id, self._string]

        if not include_node_ids:
            data.pop(1)

        return data

    # node helper #############################################################
    def remove(self):
        if not self._parent:
            raise RuntimeError('node has no parent node')

        self._parent.remove(self)

    def get_text(self):
        return self._string
