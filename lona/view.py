class LonaView:
    def __init__(self, server, view_runtime):
        self.server = server
        self.view_runtime = view_runtime

    def handle_user_enter(self, request):
        pass

    def handle_request(self, *args, **kwargs):
        return ''

    def handle_input_event_root(self, input_event):
        return input_event

    def handle_input_event(self, input_event):
        return input_event
