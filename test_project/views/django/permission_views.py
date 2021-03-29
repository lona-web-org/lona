from lona.contrib.django.auth import login_required
from lona import LonaView


class DjangLoginView(LonaView):
    @login_required
    def handle_request(self, request):
        return '<h1>Hello {}!</h1>'.format(request.user)
