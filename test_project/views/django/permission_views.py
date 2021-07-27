from lona.view import LonaView


class DjangLoginView(LonaView):
    DJANGO_AUTH_LOGIN_REQUIRED = True

    def handle_request(self, request):
        return '<h2>Hello {}!</h2>'.format(request.user)
