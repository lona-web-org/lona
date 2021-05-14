from lona.view import LonaView
from lona.html import H2


class ClassBasedView(LonaView):
    def handle_request(self, request):
        return H2('Class Based View')
