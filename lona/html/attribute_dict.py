from time import monotonic_ns

from lona.protocol import OPERATION, PATCH_TYPE


class AttributeDict:
    PATCH_TYPE = PATCH_TYPE.ATTRIBUTES

    def __init__(self, node, *args, **kwargs):
        self._node = node
        self._attributes = dict(*args, **kwargs)
        self._patches = []

    # dict helper #############################################################
    def keys(self):
        with self._node.lock:
            return self._attributes.keys()

    def items(self):
        with self._node.lock:
            return self._attributes.items()

    def pop(self, name):
        with self._node.lock:
            attribute = self._attributes.pop(name)

            self._patches.append([
                monotonic_ns(),
                self._node.id,
                self.PATCH_TYPE,
                OPERATION.REMOVE,
                name,
            ])

            return attribute

    def clear(self):
        with self._node.lock:
            if not self._attributes:
                return

            self._attributes.clear()
            self._patches.append([
                monotonic_ns(),
                self._node.id,
                self.PATCH_TYPE,
                OPERATION.CLEAR,
            ])

    def get(self, *args, **kwargs):
        with self._node.lock:
            return self._attributes.get(*args, **kwargs)

    def update(self, value):
        if not isinstance(value, dict):
            raise ValueError('dict required')

        with self._node.lock:
            for key, value in value.items():
                self[key] = value

    def __getitem__(self, name):
        with self._node.lock:
            return self._attributes[name]

    def __setitem__(self, name, value):
        if not isinstance(value, (int, bool, float, str)):
            raise ValueError('unsupported type: {}'.format(type(value)))

        if name in ('id', 'class', 'style'):
            raise RuntimeError(
                "Node.attributes['{}'] is not supported. "
                'Use Node.{}{} instead.'.format(
                    name, name, '_list' if name != 'style' else '')
            )

        with self._node.lock:
            if name in self._attributes and self._attributes[name] == value:
                return

            self._attributes[name] = value

            self._patches.append([
                monotonic_ns(),
                self._node.id,
                self.PATCH_TYPE,
                OPERATION.SET,
                name,
                value,
            ])

    def __delitem__(self, name):
        with self._node.lock:
            del self._attributes[name]

            self._patches.append([
                monotonic_ns(),
                self._node.id,
                self.PATCH_TYPE,
                OPERATION.REMOVE,
                name,
            ])

    def __eq__(self, other):
        with self._node.lock:
            if isinstance(other, self.__class__):
                other = other._attributes

        return self._attributes == other

    def __iter__(self):
        with self._node.lock:
            return self._attributes.__iter__()

    def __bool__(self):
        with self._node.lock:
            return bool(self._attributes)

    # serialisation ###########################################################
    def _reset(self, value):
        if not isinstance(value, dict):
            raise ValueError('unsupported type')

        for k, v in value.items():
            if not isinstance(v, (int, bool, float, str)):
                raise ValueError('unsupported type')

            if k in ('id', 'class', 'style'):
                raise RuntimeError(
                    "Node.attributes['{}'] is not supported. "
                    'Use Node.{}{} instead.'.format(
                        k, k, 'list' if k != 'style' else '')
                )

        with self._node.lock:
            self._attributes = value

            self._patches.append([
                monotonic_ns(),
                self._node.id,
                self.PATCH_TYPE,
                OPERATION.RESET,
                dict(value),
            ])

    def _has_patches(self):
        return bool(self._patches)

    def _get_patches(self):
        return list(self._patches)

    def _clear_patches(self):
        return self._patches.clear()

    def _serialize(self):
        return dict(self._attributes)

    # string representation ###################################################
    def to_attribute_string(self, skip_value=False):
        with self._node.lock:
            string = []

            for key, value in self._attributes.items():
                if skip_value and key == 'value':
                    continue

                string.append('{}="{}"'.format(key, value))

            return ' '.join(string)

    def to_sub_attribute_string(self):
        with self._node.lock:
            string = []

            for key, value in self._attributes.items():
                string.append('{}: {}'.format(key, value))

            return '; '.join(string)

    def __repr__(self):
        return '<AttributeDict({})>'.format(repr(self._attributes))


class StyleDict(AttributeDict):
    PATCH_TYPE = PATCH_TYPE.STYLE

    def __repr__(self):
        return '<StyleDict({})>'.format(repr(self._attributes))
