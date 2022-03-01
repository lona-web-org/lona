from __future__ import annotations

from lona.unique_ids import generate_unique_id
from lona.static_files import StaticFile
from lona.html.selector import Selector
from lona.state import State


class DummyLock:
    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass


class DummyDocument:
    @property
    def lock(self):
        return DummyLock()

    def add_patch(self, *args, **kwargs):
        pass


class AbstractNode:
    STATIC_FILES: list[StaticFile] = []
    _subclasses: list[type] = []

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

        cls._subclasses.append(cls)

    def __copy__(self, *args, **kwargs):
        raise RuntimeError('copy is not supported')

    def __deepcopy__(self, memo):
        raise RuntimeError('deepcopy is not supported')

    @staticmethod
    def get_all_node_classes():
        return [
            AbstractNode,
            *AbstractNode._subclasses,
        ]

    # id ######################################################################
    @property
    def id(self):
        if not hasattr(self, '_id'):
            self._id = generate_unique_id(name_space='nodes')

        return self._id

    # parent ##################################################################
    @property
    def parent(self):
        if not hasattr(self, '_parent'):
            self._parent = None

        return self._parent

    def _set_parent(self, parent):
        self._parent = parent

    # root ####################################################################
    @property
    def root(self):
        node = self

        while True:
            if node.parent is None:
                break

            node = node.parent

        return node

    # document ################################################################
    @property
    def document(self):
        _document = getattr(self.root, '_document', None)

        if not _document:
            return DummyDocument()

        return _document

    def _set_document(self, document):
        if self.parent:
            raise RuntimeError('node is no root node')

        self._document = document

    # locking #################################################################
    @property
    def lock(self):
        document = self.document

        if not document:
            return DummyLock()

        return document.lock

    # state ###################################################################
    @property
    def state(self):
        if not hasattr(self, '_state'):
            self._state = State(
                initial_data={},
                node=self,
            )

        return self._state

    # input events ############################################################
    def handle_change(self, input_event):
        return input_event

    def handle_click(self, input_event):
        return input_event

    def handle_focus(self, input_event):
        return input_event

    def handle_blur(self, input_event):
        return input_event

    def handle_input_event(self, input_event):
        if input_event.name == 'change':
            return self.handle_change(input_event)

        elif input_event.name == 'click':
            return self.handle_click(input_event)

        elif input_event.name == 'focus':
            return self.handle_focus(input_event)

        elif input_event.name == 'blur':
            return self.handle_blur(input_event)

        return input_event

    # queries #################################################################
    def iter_nodes(self, node=None):
        if node is None:
            node = self

        if hasattr(node, 'nodes'):
            for child in node.nodes:
                yield child

                for sub_child in self.iter_nodes(child):
                    yield sub_child

    def query_selector(self, raw_selector_string):
        selector = Selector(raw_selector_string)

        with self.lock:
            for node in self.iter_nodes():
                if selector.match(node):
                    return node

    def query_selector_all(self, raw_selector_string):
        selector = Selector(raw_selector_string)
        nodes = []

        with self.lock:
            for node in self.iter_nodes():
                if selector.match(node):
                    nodes.append(node)

            return nodes

    def closest(self, raw_selector_string):
        selector = Selector(raw_selector_string)

        with self.lock:
            node = self.parent

            while node is not None:
                if selector.match(node):
                    break

                node = node.parent

        return node
