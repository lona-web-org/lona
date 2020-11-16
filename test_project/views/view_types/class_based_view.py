from lona.html import H1


class ClassBasedView:
    def handle_request(self, request):
        return H1('Class Based View')
