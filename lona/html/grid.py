from lona.html.nodes import Div, Widget


class Clear(Div):
    CLASS_LIST = ['clear']


class Row(Widget):
    def __init__(self, *nodes):
        self.nodes = [
            Div(
                *nodes, Clear(),  # FIXME: keyword 'nodes' does not work
                _class='row',
            ),
        ]


class Col1(Div):
    CLASS_LIST = ['col-1']


class Col2(Div):
    CLASS_LIST = ['col-2']


class Col3(Div):
    CLASS_LIST = ['col-3']


class Col4(Div):
    CLASS_LIST = ['col-4']


class Col5(Div):
    CLASS_LIST = ['col-5']


class Col6(Div):
    CLASS_LIST = ['col-6']


class Col7(Div):
    CLASS_LIST = ['col-7']


class Col8(Div):
    CLASS_LIST = ['col-8']


class Col9(Div):
    CLASS_LIST = ['col-9']


class Col10(Div):
    CLASS_LIST = ['col-10']


class Col11(Div):
    CLASS_LIST = ['col-11']


class Col12(Div):
    CLASS_LIST = ['col-12']
