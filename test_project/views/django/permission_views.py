from lona.contrib.django.auth import login_required


@login_required
def django_login_required(request):
    return '<h1>Hello {}!</h1>'.format(request.user)
