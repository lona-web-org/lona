from lona.protocol import OPERATION


class AttributeList:
    def __init__(self, node, *args, **kwargs):
        self._node = node
        self._attributes = list(*args, **kwargs)
        self._changes = []

    # list helper #############################################################
    def add(self, attribute):
        if not isinstance(attribute, (int, bool, float, str)):
            raise ValueError('unsupported type')

        with self._node.document.lock():
            if attribute not in self._attributes:
                self._attributes.append(attribute)
                self._changes.append([OPERATION.ADD, attribute])

    def remove(self, attribute):
        with self._node.document.lock():
            if attribute in self._attributes:
                self._attributes.remove(attribute)
                self._changes.append([OPERATION.REMOVE, attribute])

    def clear(self):
        with self._node.document.lock():
            self._attributes.clear()
            self._changes.append([OPERATION.CLEAR])

    def toggle(self, attribute):
        with self._node.document.lock():
            if attribute in self._attributes:
                self.remove(attribute)

            else:
                self.add(attribute)

    def append(self, attribute):
        return self.add(attribute)

    def __len__(self):
        with self._node.document.lock():
            return len(self._attributes)

    def __bool__(self):
        with self._node.document.lock():
            return bool(self._attributes)

    def __iter__(self):
        with self._node.document.lock():
            return self._attributes.__iter__()

    # serialisation ###########################################################
    def _reset(self, value):
        if not isinstance(value, list):
            raise ValueError('unsupported type')

        for i in value:
            if not isinstance(i, (int, bool, float, str)):
                raise ValueError('unsupported type')

        with self._node.document.lock():
            self._attributes = value
            self._changes.append([OPERATION.RESET, list(value)])

    def _has_changes(self):
        return bool(self._changes)

    def _get_changes(self):
        return list(self._changes)

    def _clear_changes(self):
        return self._changes.clear()

    def _serialize(self):
        return list(self._attributes)

    # string representation ###################################################
    def __str__(self):
        with self._node.document.lock():
            return ' '.join([i for i in self._attributes])

    def __repr__(self):
        return '<AttributeList({})>'.format(repr(self._attributes))
