from lona.protocol import INPUT_EVENT_TYPE


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
            self.type = INPUT_EVENT_TYPE.CUSTOM
            self.name = event_payload[0]
            self.data = event_payload[1]
            self.node_info = event_payload[2:]

        elif event_payload[0] == INPUT_EVENT_TYPE.CLICK:
            self.type = INPUT_EVENT_TYPE.CLICK
            self.name = 'click'
            self.data = event_payload[1]
            self.node_info = event_payload[2:]

        elif event_payload[0] == INPUT_EVENT_TYPE.CHANGE:
            self.type = INPUT_EVENT_TYPE.CHANGE
            self.name = 'change'
            self.data = event_payload[1]
            self.node_info = event_payload[2:]

        elif event_payload[0] == INPUT_EVENT_TYPE.SUBMIT:
            self.type = INPUT_EVENT_TYPE.SUBMIT
            self.name = 'submit'
            self.data = event_payload[1]
            self.node_info = event_payload[2:]

        # find node
        # node info contains a lona node id
        if self.node_info[0] or self.node_info[1]:
            self.node, self.widgets = document.get_node(
                widget_id=self.node_info[0],
                node_id=self.node_info[1],
            )

        self.tag_name = self.node_info[2]
        self.id_list = (self.node_info[3] or '').split(' ')
        self.class_list = (self.node_info[4] or '').split(' ')

    def node_has_id(self, name):
        if self.node is None:
            return name in self.id_list

        return self.node.has_id(name)

    def node_has_class(self, name):
        if self.node is None:
            return name in self.class_list

        return self.node.has_class(name)
