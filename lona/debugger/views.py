from html import escape
import time

from lona.html.nodes import Div, H2, Table, THead, TBody, Tr, Th, Td, Button


def frontend(request):
    return {
        'template': 'lona/debugger/frontend.html',
    }


def index(request):
    return ''


class ViewControllerDashboard:
    def handle_request(self, request):
        view_controller = request.server.view_controller

        tbody = TBody()

        html = Div(
            H2('Running Views'),
            Table(
                THead(
                    Tr(
                        Th('User'),
                        Th('Route'),
                        Th('Match Info'),
                        Th('View'),
                        Th('Finished'),
                    ),
                ),
                tbody,
                border=1,
                style={
                    'width': '100%',
                },
            ),
        )

        while True:
            request.client.show(html)
            tbody.clear()

            for user, running_views in view_controller.running_views.items():
                for route, view in running_views.items():
                    button = Button('Stop')
                    button.view = view

                    tbody.append(
                        Tr(
                            Td(escape(str(user))),
                            Td(escape(repr(route.raw_path))),
                            Td(escape(repr(view.match_info))),
                            Td(escape(repr(view.handler))),
                            Td(escape(repr(view.is_finished))),
                        ),
                    )

            time.sleep(1)
