from lona.errors import ForbiddenError
from lona.view import LonaView


class DenyAccess(LonaView):
    def handle_user_enter(self, request):
        raise ForbiddenError()
