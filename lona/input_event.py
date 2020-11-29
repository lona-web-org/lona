from lona.protocol import InputEventType


class InputEvent:
    def __init__(self, request, event_payload, document):
        self.request = request
        self.event_payload = event_payload
        self.document = document

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
        if self.node_info[0]:
            self.node, self.widgets = document.get_node(self.node_info[0])

        self.tag_name = self.node_info[1]
        self.id_list = (self.node_info[2] or '').split(' ')
        self.class_list = (self.node_info[3] or '').split(' ')

    def node_has_id(self, name):
        if self.node is None:
            return name in self.id_list

        return self.node.has_id(name)

    def node_has_class(self, name):
        if self.node is None:
            return name in self.class_list

        return self.node.has_class(name)
