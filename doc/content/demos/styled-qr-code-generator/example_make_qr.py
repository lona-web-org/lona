"""
    Styled QR code generator

    Using Lona
"""

from lona_picocss.html import (
    InlineButton,
    TextInput,
    Label,
    HTML,
    Card,
    Img,
    H1,
)
from lona_picocss import install_picocss
import make_qr

from lona.html import Select2, Option2
from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


def select_add_options(select2_node, select_options):
    """
    helper function to populate a Select2 node with select_options

    must have:
        from lona.html import Select2, Option2

    option is the text that will used in the webpage
    value is the value returned when the user selects

    select_options = [ {"option": <option>, "value": <value> }, ... ]

    eg.
    select_options = [ {"option": "Option 1", "value": 1 }, ... ]
    """

    for item in select_options:
        select2_node.append(Option2(item["option"], value=item["value"]))


@app.route("/")
class Index(View):
    def generate_qr(self):
        """
        make a new qr code

        update img_qr src
        """

        self.img_qr.attributes["src"] = make_qr.image_src_str(
            self.textinput_url.value, self.select_qr_type.value
        )

    def handle_textinput_url_change(self, input_event):
        """
        textinput_url has changed
        generate qr code, update img_qr

        hide card_qr_img if no url
        """

        if not input_event.node.value:
            self.card_qr_img.hide()
        else:
            self.generate_qr()
            self.card_qr_img.show()

    def handle_select_qr_type_change(self, input_event):
        """
        qr_type has changed

        generate qr code, update img_qr
        """

        self.generate_qr()
        self.card_qr_img.show()

    def handle_request(self, request):
        # img (qr image)
        self.img_qr = Img(
            # center the qr image
            _style={"display": "block", "margin-left": "auto", "margin-right": "auto"}
        )

        # textinput (url)
        self.textinput_url = TextInput(
            placeholder="eg. https://example.com",
            handle_change=self.handle_textinput_url_change,
        )

        # select (qr_type)
        self.select_qr_type = Select2(handle_change=self.handle_select_qr_type_change)
        select_add_options(self.select_qr_type, make_qr.select_options())

        # card for qr code (for qr_img)
        self.card_qr_img = Card(self.img_qr)
        # initally, hide card_qr_img, show it when user clicks button to generate qr
        self.card_qr_img.hide()

        # card for qr code parameters (url, qr_type)
        self.card_qr_inputs = Card(
            Label("URL ", self.textinput_url),
            Label("QR Type ", self.select_qr_type),
        )

        return HTML(
            H1("Styled QR Code Generator"),
            self.card_qr_inputs,
            self.card_qr_img,
        )


if __name__ == '__main__':
    app.run()
