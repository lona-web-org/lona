import time

from lona.html.selector import Selector


class DummyLock:
    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass


class AbstractNode:
    @classmethod
    def gen_id(cls):
        return time.monotonic_ns()

    @property
    def parent(self):
        if not hasattr(self, '_parent'):
            self._parent = None

        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def root(self):
        node = self

        while True:
            if node.parent is None:
                break

            node = node.parent

        return node

    def _get_document(self):
        return getattr(self.root, '_document', None)

    def _set_document(self, document):
        if self.parent:
            raise RuntimeError('node is no rooot node')

        self._document = document

    @property
    def lock(self):
        document = self._get_document()

        if not document:
            return DummyLock()

        return document.lock

    def __copy__(self, *args, **kwargs):
        raise RuntimeError('copy is not supported')

    def __deepcopy__(self, memo):
        raise RuntimeError('deepcopy is not supported')

    # queries #################################################################
    def iter_nodes(self, node=None):
        node = node or self

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
