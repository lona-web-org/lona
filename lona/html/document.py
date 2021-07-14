from threading import RLock

from lona.html.abstract_node import AbstractNode
from lona.html.patches import PatchStack
from lona.html.widget import Widget
from lona.protocol import DATA_TYPE
from lona.html.node import Node


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
    def get_node(self, node_id, widget_id=None):
        if isinstance(node_id, Node):
            node_id = node_id.id

        value = [None, [], ]
        widget = [None]
        widget_path = []

        def iter_nodes(node):
            if isinstance(node, Widget):
                widget_path.append(node)

                if widget_id and node.id == widget_id:
                    widget[0] = node

            if isinstance(node, (Node, Widget)):
                if node.id == node_id:
                    value[0] = node
                    value[1].extend(widget_path)

                    return

                if node.nodes:
                    for i in node.nodes:
                        iter_nodes(i)

            if isinstance(node, Widget):
                widget_path.pop()

        with self.lock:
            iter_nodes(self.html)

        if widget[0]:
            value[1].append(widget[0])

        return tuple(value)

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
