from lona import LonaView
from lona.html import H1


class ClassBasedView(LonaView):
    def handle_request(self, request):
        return H1('Class Based View')
