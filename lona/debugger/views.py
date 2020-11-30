import time

from lona.html.nodes import Div, H2, Table, THead, TBody, Tr, Th, Td


def frontend(request):
    return {
        'template': 'lona/debugger/frontend.html',
    }


def index(request):
    return ''


class ViewControllerDashboard:
    def handle_request(self, request):
        view_runtime_controller = request.server.view_runtime_controller

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

            for user, view_runtimes in \
                    view_runtime_controller.running_single_user_views.items():

                for view_runtime in view_runtimes:
                    tbody.append(
                        Tr(
                            Td(str(user)),
                            Td(repr(view_runtime.route)),
                            Td(repr(view_runtime.match_info)),
                            Td(repr(view_runtime.view)),
                            Td(repr(view_runtime.is_stopped)),
                        ),
                    )

            time.sleep(1)
