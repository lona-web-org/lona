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
from lona.html import CLICK, HTML, Ul, Li, H2, P, A


class InteractiveView(View):
    def handle_request(self, request):
        html = HTML(
            H2('Interactive Response'),
            Ul(
                Li(
                    A(
                        'Empty Response',
                        href='#',
                        id='empty-response',
                        events=[CLICK],
                    ),
                ),
                Li(
                    A(
                        'Node Response',
                        href='#',
                        id='node-response',
                        events=[CLICK],
                    ),
                ),
                Li(
                    A(
                        'String Response',
                        href='#',
                        id='string-response',
                        events=[CLICK],
                    ),
                ),
                Li(
                    A(
                        'Template Response',
                        href='#',
                        id='template-response',
                        events=[CLICK],
                    ),
                ),
                Li(
                    A(
                        'Template String Response',
                        href='#',
                        id='template-string-response',
                        events=[CLICK],
                    ),
                ),
                Li(
                    A(
                        'Redirect Response',
                        href='#',
                        id='redirect-response',
                        events=[CLICK],
                    ),
                ),
                Li(
                    A(
                        'HTTP Redirect Response',
                        href='#',
                        id='http-redirect-response',
                        events=[CLICK],
                    ),
                ),
                Li(
                    A(
                        'File Response',
                        href='#',
                        id='file-response',
                        events=[CLICK],
                    ),
                ),
                Li(
                    A(
                        'JSON Response',
                        href='#',
                        id='json-response',
                        events=[CLICK],
                    ),
                ),
                Li(
                    A(
                        'Binary Response',
                        href='#',
                        id='binary-response',
                        events=[CLICK],
                    ),
                ),
                Li(
                    A(
                        'Custom Header Response',
                        href='',
                        id='custom-headers-response',
                        events=[CLICK],
                    ),
                ),
            ),
        )

        input_event = self.await_input_event(html=html)

        # no response
        if input_event.node_has_id('empty-response'):
            self.show(' ')  # FIXME: empty strings get handled like NoneTypes

            return

        # node response
        if input_event.node_has_id('node-response'):
            return P('Node Response')

        # string response
        if input_event.node_has_id('string-response'):
            return HtmlResponse('String Response')

        # template response
        if input_event.node_has_id('template-response'):
            return TemplateResponse(
                'template_response.html',
                {
                    'test_variable': 'foo',
                },
            )

        # template string response
        if input_event.node_has_id('template-string-response'):
            return TemplateStringResponse(
                '{{ message }}',
                {
                    'message': 'Template String Response',
                },
            )

        # redirect
        if input_event.node_has_id('redirect-response'):
            return RedirectResponse('/')

        # http redirect
        if input_event.node_has_id('http-redirect-response'):
            return HttpRedirectResponse('/')

        # unsupported responses
        # file Response
        if input_event.node_has_id('file-response'):
            path = os.path.join(
                os.path.dirname(__file__),
                '../../../doc/content/logo.svg',
            )

            return FileResponse(path)

        # json response
        if input_event.node_has_id('json-response'):
            return JsonResponse({'foo': 'bar'})

        # binary response
        if input_event.node_has_id('binary-response'):
            path = os.path.join(
                os.path.dirname(__file__),
                '../../../doc/content/logo.svg',
            )

            return Response(
                content_type='image/svg+xml',
                body=open(path, 'rb').read(),
            )

        # custom header response
        if input_event.node_has_id('custom-headers-response'):
            return Response(
                status=418,
                headers={
                    'HEADER-1': 'foo',
                    'HEADER-2': 'bar',
                },
                text='Custom Headers Response',
            )

        raise RuntimeError('unknown link was clicked')
