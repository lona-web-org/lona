from lona import LonaView


class DjangLoginView(LonaView):
    def handle_user_enter(self, user):
        return user.is_active and user.is_authenticated

    def handle_request(self, request):
        return '<h1>Hello {}!</h1>'.format(request.user)
