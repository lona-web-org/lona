from threading import RLock

from lona.html.abstract_node import AbstractNode
from lona.html.widget import Widget
from lona.protocol import DATA_TYPE
from lona.html.node import Node


class Document:
    def __init__(self):
        self._lock = RLock()
        self.html = None

    @property
    def lock(self):
        return self._lock

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

    def _has_changes(self):
        def has_changes(node):
            if node._has_changes():
                return True

            if hasattr(node, 'nodes'):
                for sub_node in node.nodes:
                    if has_changes(sub_node):
                        return True

            return False

        return has_changes(self.html)

    def _collect_changes(self):
        changes = []
        changed_widgets = []
        widget_path = []

        # find changes and changed widgets
        def add_changes(node):
            node_is_widget = isinstance(node, Widget)

            if node_is_widget:
                widget_path.append(node.id)

            # changed widgets
            if node_is_widget:
                if node.nodes._has_changes():
                    changed_widgets.extend(widget_path)

            elif node._has_changes():
                changed_widgets.extend(widget_path)

            # changes
            if node._has_changes():
                changes.extend(node._get_changes())

            if hasattr(node, 'nodes'):
                for sub_node in node.nodes:
                    add_changes(sub_node)

            if node_is_widget:
                widget_path.remove(node.id)

        add_changes(self.html)

        # sort changes by timestamp
        changes = sorted(changes, key=lambda x: x[0])

        # remove timestamps
        cleaned_changes = []

        for change in changes:
            cleaned_changes.append(change[1:])

        # clean list of changed widgets
        cleaned_changed_widgets = []

        for widget_id in changed_widgets[::-1]:
            if widget_id not in cleaned_changed_widgets:
                cleaned_changed_widgets.append(widget_id)

        return [cleaned_changes, cleaned_changed_widgets]

    def serialize(self):
        if not self.html:
            return self.apply('')

        return DATA_TYPE.HTML_TREE, self.html._serialize()

    def apply(self, html):
        if isinstance(html, str) and html is self.html:
            return

        # HTML update
        elif html is self.html:
            if not self._has_changes():
                return

            changes = self._collect_changes()
            self.html._clear_changes()

            return DATA_TYPE.HTML_UPDATE, changes

        # HTML
        else:
            if isinstance(self.html, AbstractNode):
                self.html._set_document(None)

            # node tree
            if isinstance(html, AbstractNode):
                self.html = html

                self.html._set_document(self)
                self.html._clear_changes()

                return self.serialize()

            # HTML string
            self.html = str(html)

            return DATA_TYPE.HTML, html
