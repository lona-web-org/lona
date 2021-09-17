from lona.html import Strong, THead, TBody, Table, Tr, Th, Td, HTML, H1
from lona import LonaView, LonaApp

from lona_bootstrap_5 import (
    SecondaryButton,
    PrimaryButton,
    DangerButton,
    Progress,
    Modal,
)

app = LonaApp(__file__)

NAMES = [
    'Alice',
    'Bob',
    'Mallory',
    'Carl',
    'Eve',
    'Martin',
    'Hal',
    'Dave',
    'Chris',
    'Paula',
]

app.add_static_file('lona/style.css', """
    body {
        margin: 1em;
    }
""")


@app.route('/')
class LonaBootstrap5PopupView(LonaView):

    # popup callbacks #########################################################
    def delete(self, input_event):
        self.selected_tr.remove()
        self.modal.hide()

    def close_popup(self, input_event):
        self.modal.hide()

    def open_delete_popup(self, input_event):
        with self.html.lock:
            self.selected_tr = input_event.node.closest('tr')
            name = self.selected_tr.nodes[0].get_text()

            # close button
            self.modal.handle_click = self.close_popup

            # modal content
            self.modal.set_title('Delete')

            self.modal.set_body(
                'Do you really want to delete ',
                Strong(name),
                '?',
            )

            # modal buttons
            self.modal.set_buttons(
                DangerButton('Delete', handle_click=self.delete),
                SecondaryButton('Cancel', handle_click=self.close_popup)
            )

            # show popup
            self.modal.show()

    # request handling ########################################################
    def handle_request(self, request):
        self.modal = Modal(centered=True)

        self.html = HTML(
            H1('Bootstrap 5 Confirmation Popup'),

            Progress(
                value=0,
                _style={
                    'width': '30em',
                    'float': 'left',
                    'margin-top': '0.5em',
                    'margin-right': '1em',
                }
            ),

            PrimaryButton('Generate Name List', _id='generate'),

            Table(
                _class='table',
                nodes=[
                    THead(
                        Tr(
                            Th('Name', width='50%'),
                            Th('Action', width='50%'),
                        )
                    ),
                    TBody()
                ]
            ),

            self.modal,
        )

        # generate name list
        generate_button = self.html.query_selector('#generate')

        self.await_click(generate_button, html=self.html)

        progress = self.html.query_selector('.progress')
        tbody = self.html.query_selector('tbody')

        for index, name in enumerate(NAMES):
            progress.set_percentage((index + 1) * 10)

            tbody.append(
                Tr(
                    Td(name),
                    Td(
                        DangerButton(
                            'Delete',
                            handle_click=self.open_delete_popup,
                        ),
                    )
                )
            )

            self.show()
            self.sleep(0.5)

        generate_button.disabled = True

        return self.html


app.run(port=8080)
