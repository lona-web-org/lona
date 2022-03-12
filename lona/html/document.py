from threading import RLock

from lona.html.abstract_node import AbstractNode
from lona.html.patches import PatchStack
from lona.protocol import DATA_TYPE


class Document:
    def __init__(self):
        self.title = ''
        self.html = None
        self._lock = RLock()
        self._patch_stack = PatchStack()

    @property
    def lock(self):
        return self._lock

    @property
    def is_dirty(self):
        return self._patch_stack.has_patches()

    def add_patch(self, *args, **kwargs):
        self._patch_stack.add_patch(*args, **kwargs)

    # html ####################################################################
    def get_node(self, node_id):
        node = None
        nodes = []

        with self.lock:
            if self.html.id == node_id:
                node = self.html

            else:
                for _node in self.html.iter_nodes():
                    if _node.id == node_id:
                        node = _node

                        break

            if node is None:
                return []

            while node is not None:
                nodes.append(node)
                node = node.parent

        return nodes

    def serialize(self):
        if not self.html:
            return self.apply(html='')

        # HTML string
        if isinstance(self.html, str):
            return self.title, DATA_TYPE.HTML, self.html

        # HTML tree
        return self.title, DATA_TYPE.HTML_TREE, self.html._serialize()

    def apply(self, title='', html=None):
        if title:
            self.title = title

        if html is None:
            return self.title, None, None

        # HTML update
        elif html is self.html:
            if not self._patch_stack.has_patches():
                return self.title, None, None

            patches = self._patch_stack.get_patches()
            self._patch_stack.clear()

            return self.title, DATA_TYPE.HTML_UPDATE, patches

        # HTML
        else:
            self._patch_stack.clear()

            if isinstance(self.html, AbstractNode):
                self.html._set_document(None)

            # node tree
            if isinstance(html, AbstractNode):
                self.html = html

                self.html._set_document(self)

                return self.title, DATA_TYPE.HTML_TREE, self.html._serialize()

            # HTML string
            self.html = str(html)

            return self.title, DATA_TYPE.HTML, html
