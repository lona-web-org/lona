from threading import RLock

from lona.html.abstract_node import AbstractNode
from lona.html.patches import PatchStack
from lona.protocol import DATA_TYPE


class Document:
    def __init__(self):
        self._lock = RLock()
        self.html = None
        self._patch_stack = PatchStack()

    @property
    def lock(self):
        return self._lock

    def add_patch(self, *args, **kwargs):
        self._patch_stack.add_patch(*args, **kwargs)

    # html ####################################################################
    def get_node(self, node_id):
        node = None
        nodes = []

        with self.lock:
            for _node in self.html.iter_nodes():
                if _node.id == node_id:
                    node = _node

                    break

            if not node:
                return []

            while node.parent is not None:
                nodes.append(node)
                node = node.parent

        return nodes

    def serialize(self):
        if not self.html:
            return self.apply('')

        return DATA_TYPE.HTML_TREE, self.html._serialize()

    def apply(self, html):
        if isinstance(html, str) and html is self.html:
            return

        # HTML update
        elif html is self.html:
            if not self._patch_stack.has_patches():
                return

            patches = self._patch_stack.get_patches()
            self._patch_stack.clear()

            return DATA_TYPE.HTML_UPDATE, patches

        # HTML
        else:
            self._patch_stack.clear()

            if isinstance(self.html, AbstractNode):
                self.html._set_document(None)

            # node tree
            if isinstance(html, AbstractNode):
                self.html = html

                self.html._set_document(self)

                return self.serialize()

            # HTML string
            self.html = str(html)

            return DATA_TYPE.HTML, html
