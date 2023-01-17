import os

from lona import (
    TemplateStringResponse,
    HttpRedirectResponse,
    TemplateResponse,
    RedirectResponse,
    JsonResponse,
    HtmlResponse,
    FileResponse,
    Response,
    View,
)
from lona.html import HTML, Ul, Li, H2, P, A


class NonInteractiveView(View):
    def handle_request(self, request):
        html = HTML(
            H2('Non-Interactive Response'),
            Ul(
                Li(
                    A(
                        'Empty Response',
                        href='/responses/non-interactive/empty-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Node Response',
                        href='/responses/non-interactive/node-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'String Response',
                        href='/responses/non-interactive/string-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Template Response',
                        href='/responses/non-interactive/template-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Template String Response',
                        href='/responses/non-interactive/template-string-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Redirect Response',
                        href='/responses/non-interactive/redirect-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'HTTP Redirect Response',
                        href='/responses/non-interactive/http-redirect-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'File Response',
                        href='/responses/non-interactive/file-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'JSON Response',
                        href='/responses/non-interactive/json-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Binary Response',
                        href='/responses/non-interactive/binary-response',
                        interactive=False,
                    ),
                ),
                Li(
                    A(
                        'Custom Headers Response',
                        href='/responses/non-interactive/custom-headers-response',
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
        return HtmlResponse('String Response')


class TemplateResponseView(View):
    def handle_request(self, request):
        return TemplateResponse(
            'template_response.html',
            {
                'test_variable': 'foo',
            },
        )


class TemplateStringResponseView(View):
    def handle_request(self, request):
        return TemplateStringResponse(
            '{{ message }}',
            {
                'message': 'Template String Response',
            },
        )


class RedirectResponseView(View):
    def handle_request(self, request):
        return RedirectResponse('/')


class HttpRedirectResponseView(View):
    def handle_request(self, request):
        return HttpRedirectResponse('/')


class FileResponseView(View):
    def handle_request(self, request):
        path = os.path.join(
            os.path.dirname(__file__),
            '../../../doc/content/logo.svg',
        )

        return FileResponse(path)


class JsonResponseView(View):
    def handle_request(self, request):
        return JsonResponse({'foo': 'bar'})


class BinaryResponseView(View):
    def handle_request(self, request):
        path = os.path.join(
            os.path.dirname(__file__),
            '../../../doc/content/logo.svg',
        )

        return Response(
            content_type='image/svg+xml',
            body=open(path, 'rb').read(),
        )


class CustomHeadersResponseView(View):
    def handle_request(self, request):
        return Response(
            status=418,
            headers={
                'HEADER-1': 'foo',
                'HEADER-2': 'bar',
            },
            text='Custom Headers Response',
        )
