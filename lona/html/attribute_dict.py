from lona.protocol import OPERATION


class AttributeDict:
    def __init__(self, node, *args, **kwargs):
        self._node = node
        self._attributes = dict(*args, **kwargs)
        self._changes = []

    # dict helper #############################################################
    def keys(self):
        with self._node.document.lock:
            return self._attributes.keys()

    def items(self):
        with self._node.document.lock:
            return self._attributes.items()

    def pop(self, name):
        with self._node.document.lock:
            self._changes.append([OPERATION.REMOVE, name])

            return self._attributes.pop(name)

    def clear(self):
        with self._node.document.lock:
            self._attributes.clear()
            self._changes.append([OPERATION.CLEAR])

    def get(self, *args, **kwargs):
        with self._node.document.lock:
            return self._attributes.get(*args, **kwargs)

    def __getitem__(self, name):
        with self._node.document.lock:
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

        with self._node.document.lock:
            self._attributes[name] = value
            self._changes.append([OPERATION.SET, name, value])

    def __delitem__(self, name):
        with self._node.document.lock:
            del self._attributes[name]
            self._changes.append([OPERATION.REMOVE, name])

    def __iter__(self):
        with self._node.document.lock:
            return self._attributes.__iter__()

    def __bool__(self):
        with self._node.document.lock:
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

        with self._node.document.lock:
            self._attributes = value
            self._changes.append([OPERATION.RESET, dict(value)])

    def _has_changes(self):
        return bool(self._changes)

    def _get_changes(self):
        return list(self._changes)

    def _clear_changes(self):
        return self._changes.clear()

    def _serialize(self):
        return dict(self._attributes)

    # string representation ###################################################
    def to_attribute_string(self):
        with self._node.document.lock:
            string = []

            for key, value in self._attributes.items():
                string.append('{}="{}"'.format(key, value))

            return ' '.join(string)

    def to_sub_attribute_string(self):
        with self._node.document.lock:
            string = []

            for key, value in self._attributes.items():
                string.append('{}: {}'.format(key, value))

            return '; '.join(string)

    def __repr__(self):
        return '<AttributeDict({})>'.format(repr(self._attributes))
