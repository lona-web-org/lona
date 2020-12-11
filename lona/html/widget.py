from lona.html.abstract_node import AbstractNode
from lona.html.node_list import NodeList
from lona.protocol import NODE_TYPE


class Widget(AbstractNode):
    @property
    def nodes(self):
        if not hasattr(self, '_nodes'):
            self._nodes = NodeList(self)

        return self._nodes

    @nodes.setter
    def nodes(self, value):
        if not hasattr(self, '_nodes'):
            self._nodes = NodeList(self)

        self._nodes._reset(value)

    @property
    def _id(self):
        if not hasattr(self, '_id_'):
            self._id_ = self.gen_id()

        return self._id_

    def __len__(self):
        return self._nodes.__len__()

    # node helper #############################################################
    def remove(self):
        if not self._parent:
            raise RuntimeError('node has no parent node')

        self._parent.remove(self)

    # serialisation ###########################################################
    def _has_changes(self):
        return self._nodes._has_changes()

    def _get_changes(self):
        return [
            self._id,
            self._nodes._get_changes(),
        ]

    def _clear_changes(self):
        self._nodes._clear_changes()

    def _serialize(self):
        return [
            NODE_TYPE.WIDGET,
            self._id,
            self.nodes._serialize(),
        ]

    # event handling ##########################################################
    def on_click(self, input_event):
        return input_event

    def on_change(self, input_event):
        return input_event

    def on_submit(self, input_event):
        return input_event

    def handle_input_event(self, input_event):
        if input_event.name == 'click':
            return self.on_click(input_event)

        elif input_event.name == 'change':
            return self.on_change(input_event)

        elif input_event.name == 'submit':
            return self.on_submit(input_event)

        return input_event

    # string representation ###################################################
    def __str__(self):
        return '<!--lona-widget:{}-->\n{}\n<!--end-lona-widget:{}-->'.format(
            self._id,
            str(self._nodes),
            self._id,
        )

    def __repr__(self):
        return self.__str__()
