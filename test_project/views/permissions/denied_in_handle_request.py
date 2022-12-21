from lona.errors import ForbiddenError
from lona.view import View


class DenyAccess(View):
    def handle_request(self, request):
        raise ForbiddenError()
