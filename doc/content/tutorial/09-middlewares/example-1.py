from lona_picocss import install_picocss

from lona import ForbiddenError, View, App
from lona.html import HTML, H1, P

app = App(__file__)

install_picocss(app, debug=True)


@app.middleware
class PasswordMiddleware:
    DATABASE = {
        '1234': 'Alice',
        'test': 'Bob',
    }

    def handle_request(self, data):
        request = data.request
        password = request.GET.get('p', '')

        if password not in self.DATABASE:
            raise ForbiddenError('You are not allowed here')

        request.user.username = self.DATABASE[password]

        return data


@app.route('/')
class Index(View):
    def handle_request(self, request):
        return HTML(
            H1(f'Hello {request.user.username}'),
            P('Welcome Back'),
        )


app.run()
