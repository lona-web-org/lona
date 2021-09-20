from lona.protocol import PATCH_TYPE, OPERATION


class AttributeList:
    PATCH_TYPE: PATCH_TYPE

    def __init__(self, node, *args, **kwargs):
        self._node = node
        self._attributes = set(*args, **kwargs)

    # list helper #############################################################
    def add(self, attribute):
        if not isinstance(attribute, (int, bool, float, str)):
            raise ValueError(f'unsupported type: {type(attribute)}')

        with self._node.lock:
            if attribute in self._attributes:
                return

            self._attributes.add(attribute)

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.ADD,
                payload=[
                    attribute,
                ],
            )

    def remove(self, attribute):
        with self._node.lock:
            if attribute not in self._attributes:
                return

            self._attributes.remove(attribute)

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.REMOVE,
                payload=[
                    attribute,
                ],
            )

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

    def toggle(self, attribute):
        with self._node.lock:
            if attribute in self._attributes:
                self.remove(attribute)

            else:
                self.add(attribute)

    def append(self, attribute):
        return self.add(attribute)

    def extend(self, attributes):
        with self._node.lock:
            for attribute in iter(attributes):
                self.add(attribute)

    def __eq__(self, other):
        with self._node.lock:
            if isinstance(other, self.__class__):
                other = other._attributes

            elif not isinstance(other, (list, set, tuple)):
                return False

            return self._attributes == set(other)

    def __len__(self):
        with self._node.lock:
            return len(self._attributes)

    def __bool__(self):
        with self._node.lock:
            return bool(self._attributes)

    def __iter__(self):
        with self._node.lock:
            return self._attributes.__iter__()

    def __contains__(self, attribute):
        with self._node.lock:
            return attribute in self._attributes

    @property
    def _list(self):
        with self._node.lock:
            return sorted(self._attributes)

    # serialization ###########################################################
    def _reset(self, value):
        if not isinstance(value, list):
            raise ValueError(f'unsupported type: {type(value)}')

        for i in value:
            if not isinstance(i, (int, bool, float, str)):
                raise ValueError(f'unsupported type: {type(i)}')

        with self._node.lock:
            self._attributes = set(value)

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=self.PATCH_TYPE,
                operation=OPERATION.RESET,
                payload=[
                    list(value),
                ],
            )

    def _serialize(self):
        return self._list

    # string representation ###################################################
    def __str__(self):
        return ' '.join(self._list)

    def __repr__(self):
        return f'<AttributeList({self._list!r})>'


class IDList(AttributeList):
    PATCH_TYPE = PATCH_TYPE.ID_LIST

    def __repr__(self):
        return f'<IDList({self._list!r})>'


class ClassList(AttributeList):
    PATCH_TYPE = PATCH_TYPE.CLASS_LIST

    def __repr__(self):
        return f'<ClassList({self._list!r})>'
