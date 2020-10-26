from datetime import datetime

from lona.html.document import Document

_default_document = Document(default_document=True)


class AbstractNode:
    @classmethod
    def gen_id(cls):
        return str(datetime.timestamp(datetime.now())).replace('.', '')

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

    def lock(self):
        return self.document.lock()
