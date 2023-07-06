from collections.abc import Iterable

from lona.html.abstract_node import AbstractNode
from lona.protocol import PATCH_TYPE, OPERATION
from lona.html.text_node import TextNode


class NodeList:
    def __init__(self, node):
        self._node = node
        self._nodes = []
        self._frozen = False

    def _freeze(self):
        self._frozen = True

    def _assert_not_frozen(self):
        if self._frozen:
            raise RuntimeError('Cannot modify frozen NodeList')

    # list helper #############################################################
    def _check_value(self, value):
        if not isinstance(value, (AbstractNode, str, int, float, bool)):
            raise ValueError(f'unsupported type: {type(value)}')

    def _prepare_node(self, node):
        if isinstance(node, (str, int, float, bool)):
            node = TextNode(node)

        if node.parent:
            node.parent.remove(node)

        if node.root is self._node.root:
            raise RuntimeError('loop detected')

        node._set_parent(self._node)

        return node

    def insert(self, index, value):
        self._assert_not_frozen()
        self._check_value(value)

        with self._node.lock:
            node = self._prepare_node(value)

            self._nodes.insert(index, node)

            index = self._nodes.index(node)

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=PATCH_TYPE.NODES,
                operation=OPERATION.INSERT,
                payload=[
                    index,
                    node._serialize(),
                ],
            )

    def append(self, value):
        self._assert_not_frozen()
        self._check_value(value)

        with self._node.lock:
            node = self._prepare_node(value)

            self._nodes.append(node)

            index = len(self._nodes) - 1

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=PATCH_TYPE.NODES,
                operation=OPERATION.INSERT,
                payload=[
                    index,
                    node._serialize(),
                ],
            )

    def extend(self, nodes):
        self._assert_not_frozen()

        with self._node.lock:
            for node in nodes:
                self.append(node)

    def remove(self, node):
        self._assert_not_frozen()

        with self._node.lock:
            self._nodes.remove(node)

            node._set_parent(None)

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=PATCH_TYPE.NODES,
                operation=OPERATION.REMOVE,
                payload=[
                    node.id,
                ],
            )

    def pop(self, index):
        self._assert_not_frozen()

        with self._node.lock:
            node = self._nodes.pop(index)

            node._set_parent(None)

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=PATCH_TYPE.NODES,
                operation=OPERATION.REMOVE,
                payload=[
                    node.id,
                ],
            )

            return node

    def clear(self):
        self._assert_not_frozen()

        with self._node.lock:
            if not self._nodes:
                return

            for node in list(self._nodes):
                node._set_parent(None)

            self._nodes.clear()

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=PATCH_TYPE.NODES,
                operation=OPERATION.CLEAR,
                payload=[],
            )

    def index(self, node):
        with self._node.lock:
            return self._nodes.index(node)

    def __getitem__(self, index):
        with self._node.lock:
            return self._nodes[index]

    def __setitem__(self, index, value):
        self._assert_not_frozen()
        self._check_value(value)

        with self._node.lock:

            # unmounting old node
            old_node = self._nodes[index]

            old_node._set_parent(None)

            # mounting new node
            node = self._prepare_node(value)

            self._nodes[index] = node

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=PATCH_TYPE.NODES,
                operation=OPERATION.SET,
                payload=[
                    index,
                    node._serialize(),
                ],
            )

    def __eq__(self, other):
        with self._node.lock:
            if isinstance(other, self.__class__):
                other = other._nodes

            elif not isinstance(other, (list, tuple, set)):
                return False

            if not len(self._nodes) == len(other):
                return False

            for index, node in enumerate(self._nodes):
                if node != other[index]:
                    return False

            return True

    def __in__(self, other):
        with self._node.lock:
            return other in self._nodes

    def __bool__(self):
        with self._node.lock:
            return bool(self._nodes)

    def __len__(self):
        with self._node.lock:
            return self._nodes.__len__()

    def __iter__(self):
        with self._node.lock:
            return self._nodes.__iter__()

    def __contains__(self, node):
        with self._node.lock:
            for child_node in self._nodes:
                if child_node is node:
                    return True

            return False

    # serialization ###########################################################
    def _reset(self, values):
        self._assert_not_frozen()

        if (isinstance(values, AbstractNode) or
                not isinstance(values, Iterable)):

            values = [values]

        with self._node.lock:
            for node in self._nodes:
                node._set_parent(None)

            self._nodes.clear()

            for value in values:
                self._check_value(value)

                node = self._prepare_node(value)

                self._nodes.append(node)

            self._node.document.add_patch(
                node_id=self._node.id,
                patch_type=PATCH_TYPE.NODES,
                operation=OPERATION.RESET,
                payload=[
                    [i._serialize() for i in self._nodes],
                ],
            )

    def _serialize(self, include_node_ids=True):
        return [i._serialize(include_node_ids=include_node_ids)
                for i in self._nodes]

    # string representation ###################################################
    def __str__(self):
        with self._node.lock:
            return '\n'.join([str(i) for i in self._nodes])

    def __repr__(self):
        return f'<NodeList({self._nodes!r}))>'
