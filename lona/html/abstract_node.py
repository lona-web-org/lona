from lona.html.selector import Selector
from lona._time import monotonic_ns


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
    def __copy__(self, *args, **kwargs):
        raise RuntimeError('copy is not supported')

    def __deepcopy__(self, memo):
        raise RuntimeError('deepcopy is not supported')

    # id ######################################################################
    @property
    def id(self):
        if not hasattr(self, '_id'):
            self._id = str(monotonic_ns())

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
            raise RuntimeError('node is no rooot node')

        self._document = document

    # locking #################################################################
    @property
    def lock(self):
        document = self.document

        if not document:
            return DummyLock()

        return document.lock

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
