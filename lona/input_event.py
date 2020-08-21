from lona.protocol import InputEventType
from lona.html.nodes import Node


class InputEvent:
    # TODO: add smart comparisons ('click' vs. 'Click')
    # TODO: rename InputEvent.input_event_type

    def __init__(self, event_payload, html):
        self.data = {}
        self.node = None
        self.widgets = []
        self.tag_name = ''
        self.id_list = []
        self.class_list = []

        # parse input event type
        if isinstance(event_payload[0], str):
            self.input_event_type = InputEventType.CUSTOM
            self.name = event_payload[0]
            self.data = event_payload[1]
            self.node_info = event_payload[2:]

        elif event_payload[0] == InputEventType.CLICK:
            self.input_event_type = InputEventType.CLICK
            self.name = 'click'
            self.data = event_payload[1]
            self.node_info = event_payload[2:]

        elif event_payload[0] == InputEventType.CHANGE:
            self.input_event_type = InputEventType.CHANGE
            self.name = 'change'
            self.data = event_payload[1]
            self.node_info = event_payload[2:]

        elif event_payload[0] == InputEventType.SUBMIT:
            self.input_event_type = InputEventType.SUBMIT
            self.name = 'submit'
            self.data = event_payload[1]
            self.node_info = event_payload[2:]

        # find node
        # node info contains a lona node id
        if len(self.node_info) == 1 and isinstance(html, Node):
            self.node, self.widgets = html.get_node(self.node_info[0])

            if not self.node:
                raise ValueError('invalid lona node id')

            self.tag_name = self.node.TAG_NAME
            self.id_list = self.node.id_list
            self.class_list = self.node.class_list

        # node info contains only client DOM informations
        elif len(self.node_info) == 4:
            self.tag_name = self.node_info[2]
            self.id_list = (self.node_info[3] or '').split(' ')
            self.class_list = (self.node_info[4] or '').split(' ')

        else:
            raise ValueError('invalid node info')

    def node_has_id(self, name):
        return name in self.id_list

    def node_has_class(self, name):
        return name in self.class_list
