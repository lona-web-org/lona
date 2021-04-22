from lona.errors import ForbiddenError
from lona.view import LonaView


class DenyAccess(LonaView):
    def handle_request(self, request):
        raise ForbiddenError()
