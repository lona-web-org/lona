from lona.html.forms import (
    Form as BaseForm,
    CheckboxField,
    Submit,
    Reset,
)

from lona.html.nodes import (
    Button as ButtonNode,
    Widget,
    Div,
    H5,
    P
)


# grid system #################################################################
class Row(Div):
    CLASS_LIST = ['row']


class ColMd1(Div):
    CLASS_LIST = ['col-md-1']


class ColMd2(Div):
    CLASS_LIST = ['col-md-2']


class ColMd3(Div):
    CLASS_LIST = ['col-md-3']


class ColMd4(Div):
    CLASS_LIST = ['col-md-4']


class ColMd5(Div):
    CLASS_LIST = ['col-md-5']


class ColMd6(Div):
    CLASS_LIST = ['col-md-6']


class ColMd7(Div):
    CLASS_LIST = ['col-md-7']


class ColMd8(Div):
    CLASS_LIST = ['col-md-8']


class ColMd9(Div):
    CLASS_LIST = ['col-md-9']


class ColMd10(Div):
    CLASS_LIST = ['col-md-10']


class ColMd11(Div):
    CLASS_LIST = ['col-md-11']


class ColMd12(Div):
    CLASS_LIST = ['col-md-12']


# forms #######################################################################
class Form(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if isinstance(field, CheckboxField):
                continue

            field.input.class_list.append('form-control')

        for node in self.extra_nodes:
            if isinstance(node, (Submit, Reset)):  # FIXME
                node.input.style['margin-right'] = '0.5em'
                node.input.style['margin-top'] = '0.5em'

            if isinstance(node, Submit):
                node.input.class_list.append('btn')
                node.input.class_list.append('btn-primary')

            elif isinstance(node, Reset):
                node.input.class_list.append('btn')
                node.input.class_list.append('btn-secondary')


# buttons #####################################################################
class _Button(ButtonNode):
    ATTRIBUTES = {
        'type': 'button',
    }


class Button(_Button):
    CLASS_LIST = ['btn', 'btn-primary']


class PrimaryButton(Button):
    pass


class SecondaryButton(_Button):
    CLASS_LIST = ['btn', 'btn-secondary']


class SuccessButton(_Button):
    CLASS_LIST = ['btn', 'btn-success']


class DangerButton(_Button):
    CLASS_LIST = ['btn', 'btn-danger']


class WarningButton(_Button):
    CLASS_LIST = ['btn', 'btn-warning']


class InfoButton(_Button):
    CLASS_LIST = ['btn', 'btn-info']


# popups ######################################################################
class ModalNode(Div):
    CLASS_LIST = ['modal']

    ATTRIBUTES = {
        'tabindex': '-1',
        'role': 'dialog',
        'z-index': '2000',
    }


class ModalDialogNode(Div):
    CLASS_LIST = ['modal-dialog']

    ATTRIBUTES = {
        'role': 'document',
    }


class ModalContentNode(Div):
    CLASS_LIST = ['modal-content']


class ModalHeaderNode(Div):
    CLASS_LIST = ['modal-header']


class ModalBodyNode(Div):
    CLASS_LIST = ['modal-body']


class ModalFooterNode(Div):
    CLASS_LIST = ['modal-footer']


class Modal(Widget):
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
