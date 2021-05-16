class LonaView:
    def __init__(self, server, view_runtime, request):
        self.server = server
        self._view_runtime = view_runtime
        self.request = request

    def handle_user_enter(self, request):
        pass

    def handle_request(self, *args, **kwargs):
        return ''

    def handle_input_event_root(self, input_event):
        return input_event

    def handle_input_event(self, input_event):
        return input_event
