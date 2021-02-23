import inspect
import time

from lona.html.document import Document

_default_document = Document(default_document=True)


class AbstractNode:
    @classmethod
    def get_path(cls):
        if cls.__module__.endswith('.py'):
            return cls.__module__

        return inspect.getfile(cls)

    @classmethod
    def gen_id(cls):
        return str(time.monotonic_ns())

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

    @property
    def document(self):
        return getattr(
            self.root, '_document', _default_document) or _default_document

    @document.setter
    def document(self, value):
        self._document = value

    @property
    def lock(self):
        return self.document.lock

    def __copy__(self, *args, **kwargs):
        raise RuntimeError('copy is not supported')

    def __deepcopy__(self, memo):
        raise RuntimeError('deepcopy is not supported')
