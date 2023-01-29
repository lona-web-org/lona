import os

from lona.html import HTML, Ul, Li, H2, P, A
from lona.view import View


class NonInteractiveView(View):
    def handle_request(self, request):
        html = HTML(
            H2('Non-Interactive Response (dict)'),
            Ul(
                Li(
                    A(
                        'Empty Response',
                        href='/legacy-responses/non-interactive/empty-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Node Response',
                        href='/legacy-responses/non-interactive/node-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'String Response',
                        href='/legacy-responses/non-interactive/string-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Template Response',
                        href='/legacy-responses/non-interactive/template-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Template String Response',
                        href='/legacy-responses/non-interactive/template-string-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Redirect Response',
                        href='/legacy-responses/non-interactive/redirect-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'HTTP Redirect Response',
                        href='/legacy-responses/non-interactive/http-redirect-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'File Response',
                        href='/legacy-responses/non-interactive/file-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'JSON Response',
                        href='/legacy-responses/non-interactive/json-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Binary Response',
                        href='/legacy-responses/non-interactive/binary-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Custom Header Response',
                        href='/legacy-responses/non-interactive/custom-headers-response',
                        interactive=False,
                    ),
                ),
            ),
        )

        return html


class EmptyResponseView(View):
    def handle_request(self, request):
        return


class NodeResponseView(View):
    def handle_request(self, request):
        return P('Node Response')


class StringResponseView(View):
    def handle_request(self, request):
        return 'String Response'


class TemplateResponseView(View):
    def handle_request(self, request):
        return {
            'template': 'template_response.html',
            'test_variable': 'foo',
        }


class TemplateStringResponseView(View):
    def handle_request(self, request):
        return {
            'template_string': '{{ message }}',
            'message': 'Template String Response',
        }


class RedirectResponseView(View):
    def handle_request(self, request):
        return {
            'redirect': '/',
        }


class HttpRedirectResponseView(View):
    def handle_request(self, request):
        return {
            'http_redirect': '/',
        }


class FileResponseView(View):
    def handle_request(self, request):
        path = os.path.join(
            os.path.dirname(__file__),
            '../../../doc/content/logo.svg',
        )

        return {
            'file': path,
        }


class JsonResponseView(View):
    def handle_request(self, request):
        return {
            'json': {'foo': 'bar'},
        }


class BinaryResponseView(View):
    def handle_request(self, request):
        path = os.path.join(
            os.path.dirname(__file__),
            '../../../doc/content/logo.svg',
        )

        return {
            'content_type': 'image/svg+xml',
            'body': open(path, 'rb').read(),
        }


class CustomHeadersResponseView(View):
    def handle_request(self, request):
        return {
            'status': 418,
            'headers': {
                'HEADER-1': 'foo',
                'HEADER-2': 'bar',
            },
            'text': 'Custom Headers Response',
        }
