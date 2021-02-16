from lona.html import (
    TextInput as BaseTextInput,
    Button as BaseButton,
    Widget,
    Div,
    H5,
    P
)

from lona.static_files import StaticFile, StyleSheet, SORT_ORDER


STATIC_FILES = [
    # css files
    StyleSheet(
        name='bootstrap3.css',
        path='static/css/bootstrap.min.css',
        url='bootstrap3.min.css',
        sort_order=SORT_ORDER.FRAMEWORK,
    ),
    StyleSheet(
        name='bootstrap3-theme.css',
        path='static/css/bootstrap-theme.min.css',
        url='bootstrap3-theme.min.css',
        sort_order=SORT_ORDER.FRAMEWORK,
        enabled_by_default=False,
    ),

    # map files
    StaticFile(
        name='bootstrap3.css.map',
        path='static/css/bootstrap.min.css.map',
        url='bootstrap3.min.css.map',
        link=False,
    ),
    StaticFile(
        name='bootstrap3-theme.css.map',
        path='static/css/bootstrap-theme.min.css.map',
        url='bootstrap3-theme.min.css.map',
        link=False,
    ),

    # fonts
    StaticFile(
        name='bootstrap3-glyphicons-halflings-regular.eot',
        path='static/fonts/glyphicons-halflings-regular.eot',
        url='fonts/glyphicons-halflings-regular.eot',
        link=False,
    ),
    StaticFile(
        name='bootstrap3-glyphicons-halflings-regular.svg',
        path='static/fonts/glyphicons-halflings-regular.svg',
        url='fonts/glyphicons-halflings-regular.svg',
        link=False,
    ),
    StaticFile(
        name='bootstrap3-glyphicons-halflings-regular.ttf',
        path='static/fonts/glyphicons-halflings-regular.ttf',
        url='fonts/glyphicons-halflings-regular.ttf',
        link=False,
    ),
    StaticFile(
        name='bootstrap3-glyphicons-halflings-regular.woff',
        path='static/fonts/glyphicons-halflings-regular.woff',
        url='fonts/glyphicons-halflings-regular.woff',
        link=False,
    ),
    StaticFile(
        name='bootstrap3-glyphicons-halflings-regular.woff2',
        path='static/fonts/glyphicons-halflings-regular.woff2',
        url='fonts/glyphicons-halflings-regular.woff2',
        link=False,
    ),
]


# grid system #################################################################
class Row(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['row']


class ColMd1(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-1']


class ColMd2(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-2']


class ColMd3(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-3']


class ColMd4(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-4']


class ColMd5(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-5']


class ColMd6(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-6']


class ColMd7(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-7']


class ColMd8(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-8']


class ColMd9(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-9']


class ColMd10(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-10']


class ColMd11(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-11']


class ColMd12(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['col-md-12']


# inputs ######################################################################
class TextInput(BaseTextInput):
    CLASS_LIST = ['form-control']


class InlineTextInput(TextInput):
    STYLE = {
        'width': 'auto',
        'display': 'inline',
    }


# buttons #####################################################################
class _Button(BaseButton):
    STATIC_FILES = STATIC_FILES

    ATTRIBUTES = {
        'type': 'button',
    }


class Button(_Button):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['btn', 'btn-primary']


class PrimaryButton(Button):
    STATIC_FILES = STATIC_FILES


class SecondaryButton(_Button):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['btn', 'btn-secondary']


class SuccessButton(_Button):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['btn', 'btn-success']


class DangerButton(_Button):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['btn', 'btn-danger']


class WarningButton(_Button):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['btn', 'btn-warning']


class InfoButton(_Button):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['btn', 'btn-info']


# popups ######################################################################
class ModalNode(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['modal']

    ATTRIBUTES = {
        'tabindex': '-1',
        'role': 'dialog',
        'z-index': '2000',
    }


class ModalDialogNode(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['modal-dialog']

    ATTRIBUTES = {
        'role': 'document',
    }


class ModalContentNode(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['modal-content']


class ModalHeaderNode(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['modal-header']


class ModalBodyNode(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['modal-body']


class ModalFooterNode(Div):
    STATIC_FILES = STATIC_FILES
    CLASS_LIST = ['modal-footer']


class Modal(Widget):
    STATIC_FILES = STATIC_FILES

    class Mode:
        CONFIRM = 1
        CANCEL = 2

    def __init__(self, title='', body='', mode=Mode.CONFIRM):
        self.title = H5(title, _class='modal-title')
        self.body = P(body)

        self.buttons = []
        self.model_footer = ModalFooterNode()

        self.nodes = [ModalNode(
            ModalDialogNode(
                ModalContentNode(
                    ModalHeaderNode(
                        self.title,
                    ),
                    ModalBodyNode(
                        self.body,
                    ),
                    self.model_footer,
                ),
            ),
        )]

        self.set_mode(mode)

    def set_mode(self, mode):
        if mode == self.Mode.CONFIRM:
            self.buttons = [
                PrimaryButton('OK'),
                SecondaryButton('Cancel'),
            ]

            self.buttons[0].action = 'ok'
            self.buttons[1].action = 'cancel'

        elif mode == self.Mode.CANCEL:
            self.buttons = [
                DangerButton('Cancel'),
                SecondaryButton('Continue'),
            ]

            self.buttons[0].action = 'cancel'
            self.buttons[1].action = 'continue'

        else:
            raise ValueError('unknown mode')

        self.model_footer.nodes = self.buttons

    def set_title(self, title):
        self.title.set_text(title)

    def set_body(self, body):
        self.body.set_text(body)

    def show(self):
        self.nodes[0].style['display'] = 'block'

    def hide(self):
        self.nodes[0].style['display'] = 'none'


# progress bars ###############################################################
class ProgressBar(Widget):
    STATIC_FILES = STATIC_FILES

    def __init__(self, initial_value=None):
        self.progress_bar = Div(
            _class='progress-bar',
            _role='progress-bar',
            attributes={
                'aria-valuemin': '0',
                'aria-valuemax': '100',

            },
        )

        self.nodes = [Div(
            self.progress_bar,
            _class='progress',
        )]

        if initial_value:
            self.set_value(initial_value)

    def set_value(self, value, label=''):
        if isinstance(value, (tuple, list)):
            current, total = value

            if current == total:
                percentage = '100%'

            else:
                percentage = '{}%'.format(int((current / total) * 100))

            label = '{} ({}/{})'.format(percentage, current, total)

        else:
            percentage = '{}%'.format(value)

            if not label:
                label = percentage

        self.progress_bar.attributes['aria-valuenow'] = value
        self.progress_bar.style['width'] = percentage

        if label:
            self.progress_bar.set_text(label)
