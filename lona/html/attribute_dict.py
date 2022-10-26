import html

from lona.protocol import PATCH_TYPE, OPERATION

BOOLEAN_ATTRIBUTES = [
    'allowfullscreen',
    'async',
    'autofocus',
    'autoplay',
    'checked',
    'controls',
    'default',
    'disabled',
    'formnovalidate',
    'hidden',
    'ismap',
    'itemscope',
    'loop',
    'multiple',
    'muted',
    'novalidate',
    'open',
    'playsinline',
    'readonly',
    'required',
    'reversed',
    'selected',
]


class AttributeDict:
    PATCH_TYPE = PATCH_TYPE.ATTRIBUTES

    def __init__(self, node, *args, **kwargs):
        self._node = node
        self._attributes = dict(*args, **kwargs)

    # dict helper #############################################################
    def keys(self):
        with self._node.lock:
            return self._attributes.keys()

    def items(self):
        with self._node.lock:
            return self._attributes.items()

    def pop(self, name, *default):
        if len(default) > 1:
            raise TypeError(
                f'pop expected at most 2 arguments, got {1 + len(default)}',
            )

        with self._node.lock:
            if default and name not in self._attributes:
                return default[0]

            attribute = self._attributes.pop(name)

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.REMOVE,
                payload=[
                    name,
                ],
            )

            return attribute

    def clear(self):
        with self._node.lock:
            if not self._attributes:
                return

            self._attributes.clear()

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.CLEAR,
                payload=[],
            )

    def get(self, *args, **kwargs):
        with self._node.lock:
            return self._attributes.get(*args, **kwargs)

    def update(self, value):
        if not isinstance(value, dict):
            raise ValueError('dict required')

        with self._node.lock:
            for key, _value in value.items():
                self[key] = _value

    def __getitem__(self, name):
        with self._node.lock:
            return self._attributes[name]

    def __setitem__(self, name, value, issuer=None):
        if not isinstance(value, (int, bool, float, str)):
            raise ValueError(f'unsupported type: {type(value)}')

        if name in ('id', 'class'):
            raise RuntimeError(
                f"Node.attributes['{name}'] is not supported. Use Node.{name}_list instead.",
            )

        if name == 'style':
            raise RuntimeError(
                f"Node.attributes['{name}'] is not supported. Use Node.{name} instead.",
            )

        with self._node.lock:
            if name in self._attributes and self._attributes[name] == value:
                return

            self._attributes[name] = value

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.SET,
                payload=[
                    name,
                    value,
                ],
                issuer=issuer,
            )

    def __delitem__(self, name):
        self.pop(name, None)

    def __eq__(self, other):
        with self._node.lock:
            if isinstance(other, self.__class__):
                other = other._attributes

        return self._attributes == other

    def __iter__(self):
        with self._node.lock:
            return self._attributes.__iter__()

    def __contains__(self, name):
        with self._node.lock:
            return name in self._attributes

    def __bool__(self):
        with self._node.lock:
            return bool(self._attributes)

    # serialization ###########################################################
    def _reset(self, value):
        if not isinstance(value, dict):
            raise ValueError('unsupported type')

        for name, v in value.items():
            if not isinstance(v, (int, bool, float, str)):
                raise ValueError('unsupported type')

            if name in ('id', 'class'):
                raise RuntimeError(
                    f"Node.attributes['{name}'] is not supported. Use Node.{name}_list instead.",
                )

            if name == 'style':
                raise RuntimeError(
                    f"Node.attributes['{name}'] is not supported. Use Node.{name} instead.",
                )

        with self._node.lock:
            self._attributes = value

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.RESET,
                payload=[
                    dict(value),
                ],
            )

    def _serialize(self):
        return dict(self._attributes)

    # string representation ###################################################
    def to_attribute_string(self, skip_value=False):
        with self._node.lock:
            string = []

            for key, value in self._attributes.items():
                if skip_value and key == 'value':
                    continue

                # boolean properties
                if key in BOOLEAN_ATTRIBUTES:
                    if value is not False:
                        string.append(key)

                else:
                    string.append(f'{key}="{html.escape(str(value))}"')

            return ' '.join(string)

    def to_sub_attribute_string(self):
        with self._node.lock:
            string = []

            for key, value in self._attributes.items():
                string.append(f'{key}: {html.escape(str(value))}')

            return '; '.join(string)

    def __repr__(self):
        return f'<AttributeDict({self._attributes!r})>'


class StyleDict(AttributeDict):
    PATCH_TYPE = PATCH_TYPE.STYLE

    def __repr__(self):
        return f'<StyleDict({self._attributes!r})>'
