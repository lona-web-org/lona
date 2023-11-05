from datetime import datetime

from lona_picocss.html import ScrollerPre, HTML, Grid, Div, H1, A
from lona_picocss import install_picocss
from lona_dropzone import Dropzone

from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


@app.route('/')
class DropzoneView(View):
    def handle_request(self, request):
        self.dropzone = Dropzone(
            request=request,
            on_add=self.on_add,
            on_delete=self.on_delete,
        )

        self.scroller = ScrollerPre(height='30em')

        return HTML(
            H1('Dropzone'),
            Grid(
                Div(
                    self.dropzone,
                ),
                Div(
                    self.scroller,
                    A(
                        'Bucket URL',
                        href=self.dropzone.bucket.get_url(),
                        target='_blank',
                        interactive=False,
                    ),
                ),
            ),
        )

    def on_add(self, file_names):
        # this method gets called whenever a file gets added (uploaded)

        self.scroller.append(
            f'{datetime.now()}: on_add: {file_names=}\n',
        )

        self.show()

    def on_delete(self, file_names):
        # this method gets called whenever a file gets deleted

        self.scroller.append(
            f'{datetime.now()}: on_delete: {file_names=}\n',
        )

        self.show()


if __name__ == '__main__':
    app.run()
