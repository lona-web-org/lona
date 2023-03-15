from lona.html import (
    CheckBox,
    Select,
    Button,
    Label,
    Span,
    HTML,
    Pre,
    Div,
    H3,
    H2,
)
from lona.html.widgets import HTML as LegacyHTML
from lona.compat import get_client_version
from lona.static_files import Script
from lona._json import dumps
from lona import View


def client_version(*client_versions):
    # TODO: remove in 2.0

    def decorator(step):
        step.client_versions = client_versions

        return step

    return decorator


class LegacyWidgetDataTestComponent(Div):
    WIDGET = 'LegacyWidgetDataTestWidget'

    def __init__(self, initial_state):
        super().__init__()

        self.server_state = Div(
            _id='server-widget-data',
        )

        self.nodes = [
            self.server_state,
            Div(_id='client-widget-data'),
        ]

        self.widget_data = initial_state
        self.update_state()

    def update_state(self):
        self.server_state.set_text(dumps(self.widget_data))


class WidgetDataTestComponent(LegacyWidgetDataTestComponent):
    WIDGET = 'WidgetDataTestWidget'


class HTMLConsole(Div):
    WIDGET = 'HTMLConsoleWidget'

    def __init__(self, root_node):
        super().__init__()

        self.widget_data = {
            'root_node': root_node,
            'trigger': 1,
        }

        self.nodes = [
            Console(_class='console'),
        ]

    def update(self):
        self.widget_data['trigger'] = self.widget_data['trigger'] * -1


class Spacer(Div):
    STYLE = {
        'display': 'inline-block',
        'width': '1em',
    }


class RenderingRoot(Div):
    STYLE = {
        'font-size': '16px',
        'border': '1px solid red',
        'width': '100%',
        'min-height': '20em',
        'overflow': 'auto',
    }


class Console(Pre):
    STYLE = {
        'font-size': '16px',
        'background-color': 'lightgrey',
        'border': '1px solid lightgrey',
        'width': '100%',
        'min-height': '20em',
        'padding': '0',
        'margin': '0',
        'overflow': 'auto',
    }


class LeftCol(Div):
    STYLE = {
        'min-height': '1px',
        'float': 'left',
        'width': 'calc(50% - 5px)',
    }


class RightCol(Div):
    STYLE = {
        'min-height': '1px',
        'float': 'right',
        'width': 'calc(50% - 5px)',
    }


class RenderingTestView(View):
    STATIC_FILES = [
        Script(name='RenderingTestWidgets', path='rendering-test-widgets.js'),
    ]

    def handle_mode_change(self, input_event):
        select = input_event.node

        with self.html.lock:
            self.start.disabled = not (select.value == 'auto' and
                                       not self.running)

            self.stop.disabled = not (select.value == 'auto' and self.running)

            self.next_step.disabled = select.value == 'auto'
            self.reset.disabled = self.running

    def handle_stop_click(self, input_event):
        with self.html.lock:
            self.running = False
            self.mode.disabled = False
            self.start.disabled = False
            self.stop.disabled = True
            self.reset.disabled = False

    def handle_reset_click(self, input_event):
        with self.html.lock:
            self.reset_rendering_steps()

    def handle_daemon_change(self, input_event):
        self.is_daemon = self.daemon.value

    def handle_request(self, request):

        # setup html
        self.mode = Select(
            values=[
                ('auto', 'Auto', False),
                ('manual', 'Manual', True),
            ],
            handle_change=self.handle_mode_change,
        )

        self.start = Button('Start', disabled=True)

        self.stop = Button(
            'Stop',
            disabled=True,
            handle_click=self.handle_stop_click,
        )

        self.next_step = Button('Next Step', _id='next-step')
        self.reset = Button('Reset', handle_click=self.handle_reset_click)

        self.interval = Select(
            _id='interval',
            values=[
                (1,    '1s',    False),
                (0.5,  '0.5s',  True),
                (0.25, '0.25s', False),
                (0.01, '0.01s', False),
            ],
        )

        self.daemon = CheckBox(
            value=False,
            _id='daemon',
            handle_change=self.handle_daemon_change,
        )

        self.rendering_step_label = H3(
            'Step ',
            Span(_id='current'),
            '/',
            Span(_id='total'),
            ': ',
            Span(_id='label'),
            _id='step-label',
        )

        self.rendering_root = RenderingRoot(_id='rendering-root')
        self.html_console = HTMLConsole(root_node='#rendering-root')

        self.html = HTML(
            H2('Rendering Test'),
            Div(
                self.mode,
                self.start,
                self.stop,
                self.next_step,
                self.reset,

                Spacer(),

                Label('Interval: ', _for='interval'), self.interval,

                Spacer(),

                Label('Daemon:', _for='daemon'), self.daemon,
            ),

            self.rendering_step_label,
            Div(
                LeftCol(
                    Div('Render Result'),
                    self.rendering_root,
                ),
                RightCol(
                    Div('HTML Preview'),
                    self.html_console,
                ),
            ),
        )

        self.server.state['rendering-root'] = self.rendering_root

        # setup steps
        self.reset_rendering_steps()

        # main loop
        while True:
            input_event = self.await_click(html=self.html)

            if input_event.node is self.next_step:
                self.run_next_step()

            if input_event.node is self.start:
                self.start.disabled = True
                self.stop.disabled = False
                self.mode.disabled = True
                self.reset.disabled = True
                self.running = True

                while self.running:
                    self.run_next_step()
                    self.show()
                    self.sleep(float(self.interval.value))

    # rendering steps #########################################################
    def reset_rendering_steps(self):
        with self.html.lock:
            self.running = False
            self.steps = self.get_rendering_steps()
            self.current_step_index = 0
            self.rendering_root.clear()

            self.set_step_label(0, 'Not started')
            self.html_console.update()

    def get_rendering_steps(self):
        steps = []
        client_version = get_client_version()

        for attribute_name in dir(self):
            if not attribute_name.startswith('step_'):
                continue

            step = getattr(self, attribute_name)

            if client_version not in step.client_versions:
                continue

            steps.append(step)

        return steps

    def run_next_step(self):
        with self.html.lock:
            step = self.steps[self.current_step_index]

            step()
            self.html_console.update()

            self.current_step_index += 1

            if self.current_step_index >= len(self.steps):
                self.current_step_index = 0

    def set_step_label(self, step_number, label_text):
        with self.html.lock:

            # current
            current = self.rendering_step_label.query_selector('#current')
            current.set_text(step_number)

            # total
            total = self.rendering_step_label.query_selector('#total')
            total.set_text(len(self.steps))

            # label
            label = self.rendering_step_label.query_selector('#label')
            label.set_text(label_text)

    # steps ###################################################################
    # node tests
    @client_version(1, 2)
    def step_01(self):
        self.set_step_label(1, 'Clear Nodes')

        self.rendering_root.clear()

    @client_version(1, 2)
    def step_02(self):
        self.set_step_label(2, 'Append Nodes')

        self.rendering_root.append(Div('first div'))
        self.rendering_root.append(Div('second div'))

    @client_version(1, 2)
    def step_03(self):
        self.set_step_label(3, 'Set Node')

        self.rendering_root[0] = Div('set div')

    @client_version(1, 2)
    def step_04(self):
        self.set_step_label(4, 'Reset Nodes')

        self.rendering_root.nodes = [
            Div('reset div1'),
            Div('reset div2'),
        ]

    @client_version(1, 2)
    def step_05(self):
        self.set_step_label(5, 'Insert Node')

        self.rendering_root.nodes.insert(1, Div('inserted div'))

    @client_version(1, 2)
    def step_06(self):
        self.set_step_label(6, 'Remove Node')

        self.rendering_root.nodes[1].remove()

    # id_list tests
    @client_version(1, 2)
    def step_07(self):
        self.set_step_label(7, 'Set id')

        self.rendering_root.nodes = [
            Div(_id='foo bar'),
        ]

    @client_version(1, 2)
    def step_08(self):
        self.set_step_label(8, 'Add id')

        self.rendering_root.nodes[0].id_list.add('baz')

    @client_version(1, 2)
    def step_09(self):
        self.set_step_label(9, 'Remove id')

        self.rendering_root.nodes[0].id_list.remove('bar')

    @client_version(1, 2)
    def step_10(self):
        self.set_step_label(10, 'Reset id')

        self.rendering_root.nodes[0].id_list = ['foo1', 'bar1']

    @client_version(1, 2)
    def step_11(self):
        self.set_step_label(11, 'Clear id')

        self.rendering_root.nodes[0].id_list.clear()

    # class_list tests
    @client_version(1, 2)
    def step_12(self):
        self.set_step_label(12, 'Set class')

        self.rendering_root.nodes = [
            Div(_class='foo bar'),
        ]

    @client_version(1, 2)
    def step_13(self):
        self.set_step_label(13, 'Add class')

        self.rendering_root.nodes[0].class_list.add('baz')

    @client_version(1, 2)
    def step_14(self):
        self.set_step_label(14, 'Remove class')

        self.rendering_root.nodes[0].class_list.remove('bar')

    @client_version(1, 2)
    def step_15(self):
        self.set_step_label(15, 'Reset class')

        self.rendering_root.nodes[0].class_list = ['foo1', 'bar1']

    @client_version(1, 2)
    def step_16(self):
        self.set_step_label(16, 'Clear class')

        self.rendering_root.nodes[0].class_list.clear()

    # attribute tests
    @client_version(1, 2)
    def step_17(self):
        self.set_step_label(17, 'Set attributes')

        self.rendering_root.nodes = [
            Div(foo='foo', bar='bar'),
        ]

    @client_version(1, 2)
    def step_18(self):
        self.set_step_label(18, 'Add attribute')

        self.rendering_root.nodes[0].attributes['baz'] = 'baz'

    @client_version(1, 2)
    def step_19(self):
        self.set_step_label(19, 'Remove attribute')

        del self.rendering_root.nodes[0].attributes['foo']

    @client_version(1, 2)
    def step_20(self):
        self.set_step_label(20, 'Reset attributes')

        self.rendering_root.nodes[0].attributes = {
            'foo1': 'bar1',
            'bar1': 'foo1',
        }

    @client_version(1, 2)
    def step_21(self):
        self.set_step_label(21, 'Clear attributes')

        self.rendering_root.nodes[0].attributes.clear()

    # style tests
    @client_version(1, 2)
    def step_22(self):
        self.set_step_label(22, 'Set style')

        self.rendering_root.nodes = [
            Div(_style='top: 1px; right: 2px;'),
        ]

    @client_version(1, 2)
    def step_23(self):
        self.set_step_label(23, 'Add style')

        self.rendering_root.nodes[0].style['bottom'] = '3px'

    @client_version(1, 2)
    def step_24(self):
        self.set_step_label(24, 'Remove style')

        del self.rendering_root.nodes[0].style['top']

    @client_version(1, 2)
    def step_25(self):
        self.set_step_label(25, 'Reset style')

        self.rendering_root.nodes[0].style = {
            'left': '4px',
        }

    @client_version(1, 2)
    def step_26(self):
        self.set_step_label(26, 'Clear style')

        self.rendering_root.nodes[0].style.clear()

    # legacy widget data tests
    # TODO: remove in 2.0
    @client_version(1, 2)
    def step_27(self):
        self.set_step_label(27, 'Legacy Widget Data: list: setup')

        self.rendering_root.nodes = [
            LegacyWidgetDataTestComponent(
                initial_state={'list': []},
            ),
        ]

    @client_version(1, 2)
    def step_28(self):
        self.set_step_label(28, 'Legacy Widget Data: list: append')

        component = self.rendering_root.nodes[0]

        component.widget_data['list'].append(1)
        component.widget_data['list'].append(2)
        component.widget_data['list'].append(3)
        component.update_state()

    @client_version(1, 2)
    def step_29(self):
        self.set_step_label(29, 'Legacy Widget Data: list: remove')

        component = self.rendering_root.nodes[0]

        component.widget_data['list'].remove(2)
        component.update_state()

    @client_version(1, 2)
    def step_30(self):
        self.set_step_label(30, 'Legacy Widget Data: list: insert')

        component = self.rendering_root.nodes[0]

        component.widget_data['list'].insert(0, 0)
        component.update_state()

    @client_version(1, 2)
    def step_31(self):
        self.set_step_label(31, 'Legacy Widget Data: list: clear')

        component = self.rendering_root.nodes[0]

        component.widget_data['list'].clear()
        component.update_state()

    @client_version(1, 2)
    def step_32(self):
        self.set_step_label(32, 'Legacy Widget Data: list: reset')

        component = self.rendering_root.nodes[0]

        component.widget_data['list'] = [5, 4, 3, 2, 1]
        component.update_state()

    @client_version(1, 2)
    def step_33(self):
        self.set_step_label(33, 'Legacy Widget Data: dict: setup')

        component = self.rendering_root.nodes[0]

        component.widget_data = {'dict': {}}
        component.update_state()

    @client_version(1, 2)
    def step_34(self):
        self.set_step_label(34, 'Legacy Widget Data: dict: set')

        component = self.rendering_root.nodes[0]

        component.widget_data['dict'][1] = 1
        component.widget_data['dict'][2] = 2
        component.widget_data['dict'][3] = 3
        component.update_state()

    @client_version(1, 2)
    def step_35(self):
        self.set_step_label(35, 'Legacy Widget Data: dict: del')

        component = self.rendering_root.nodes[0]

        del component.widget_data['dict'][2]
        component.update_state()

    @client_version(1, 2)
    def step_36(self):
        self.set_step_label(36, 'Legacy Widget Data: dict: pop')

        component = self.rendering_root.nodes[0]

        component.widget_data['dict'].pop(3)
        component.update_state()

    @client_version(1, 2)
    def step_37(self):
        self.set_step_label(37, 'Legacy Widget Data: dict: clear')

        component = self.rendering_root.nodes[0]

        component.widget_data['dict'].clear()
        component.update_state()

    @client_version(1, 2)
    def step_38(self):
        self.set_step_label(38, 'Legacy Widget Data: dict: reset')

        component = self.rendering_root.nodes[0]

        component.widget_data['dict'] = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
        component.update_state()

    # widget data tests
    @client_version(1, 2)
    def step_39(self):
        self.set_step_label(39, 'Widget Data: list: setup')

        self.rendering_root.nodes = [
            WidgetDataTestComponent(
                initial_state={'list': []},
            ),
        ]

    @client_version(1, 2)
    def step_40(self):
        self.set_step_label(40, 'Widget Data: list: append')

        component = self.rendering_root.nodes[0]

        component.widget_data['list'].append(1)
        component.widget_data['list'].append(2)
        component.widget_data['list'].append(3)
        component.update_state()

    @client_version(1, 2)
    def step_41(self):
        self.set_step_label(41, 'Widget Data: list: remove')

        component = self.rendering_root.nodes[0]

        component.widget_data['list'].remove(2)
        component.update_state()

    @client_version(1, 2)
    def step_42(self):
        self.set_step_label(42, 'Widget Data: list: insert')

        component = self.rendering_root.nodes[0]

        component.widget_data['list'].insert(0, 0)
        component.update_state()

    @client_version(1, 2)
    def step_43(self):
        self.set_step_label(43, 'Widget Data: list: clear')

        component = self.rendering_root.nodes[0]

        component.widget_data['list'].clear()
        component.update_state()

    @client_version(1, 2)
    def step_44(self):
        self.set_step_label(44, 'Widget Data: list: reset')

        component = self.rendering_root.nodes[0]

        component.widget_data['list'] = [5, 4, 3, 2, 1]
        component.update_state()

    @client_version(1, 2)
    def step_45(self):
        self.set_step_label(45, 'Widget Data: dict: setup')

        component = self.rendering_root.nodes[0]

        component.widget_data = {'dict': {}}
        component.update_state()

    @client_version(1, 2)
    def step_46(self):
        self.set_step_label(46, 'Widget Data: dict: set')

        component = self.rendering_root.nodes[0]

        component.widget_data['dict'][1] = 1
        component.widget_data['dict'][2] = 2
        component.widget_data['dict'][3] = 3
        component.update_state()

    @client_version(1, 2)
    def step_47(self):
        self.set_step_label(47, 'Widget Data: dict: del')

        component = self.rendering_root.nodes[0]

        del component.widget_data['dict'][2]
        component.update_state()

    @client_version(1, 2)
    def step_48(self):
        self.set_step_label(48, 'Widget Data: dict: pop')

        component = self.rendering_root.nodes[0]

        component.widget_data['dict'].pop(3)
        component.update_state()

    @client_version(1, 2)
    def step_49(self):
        self.set_step_label(49, 'Widget Data: dict: clear')

        component = self.rendering_root.nodes[0]

        component.widget_data['dict'].clear()
        component.update_state()

    @client_version(1, 2)
    def step_50(self):
        self.set_step_label(50, 'Widget Data: dict: reset')

        component = self.rendering_root.nodes[0]

        component.widget_data['dict'] = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
        component.update_state()

    # html symbols ############################################################
    @client_version(1, 2)
    def step_51(self):
        self.set_step_label(51, 'HTML Symbols')

        self.rendering_root.nodes = [
            '&euro;',
            '&#8364;',
            '&#x20AC;',
        ]

    # legacy widgets ##########################################################
    # TODO: remove in 2.0

    @client_version(1)
    def step_52(self):
        self.set_step_label(52, 'Legacy Widgets: Setup')

        self.rendering_root.clear()

        self.rendering_root.nodes = [
            LegacyHTML(
                Div('1.1'),
                Div('1.2'),
            ),
            Div('2.1'),
            LegacyHTML(
                Div('3.1'),
                Div('3.2'),
            ),
        ]

    @client_version(1)
    def step_53(self):
        self.set_step_label(53, 'Legacy Widgets: Append Nodes')

        widget1 = self.rendering_root.nodes[0]
        widget1.append(Div('1.3'))

        widget2 = self.rendering_root.nodes[2]
        widget2.append(Div('3.3'))

        self.rendering_root.append(Div('4.1'))

    @client_version(1)
    def step_54(self):
        self.set_step_label(54, 'Legacy Widgets: Set Nodes')

        widget1 = self.rendering_root.nodes[0]
        widget1.nodes[1] = Div('1.2.1')

        widget1 = self.rendering_root.nodes[2]
        widget1.nodes[1] = Div('3.2.1')

    @client_version(1)
    def step_55(self):
        self.set_step_label(55, 'Legacy Widgets: Reset Nodes')

        widget1 = self.rendering_root.nodes[0]

        widget1.nodes = [
            Div('1.1.1'),
            Div('1.2.1'),
            Div('1.3.1'),
        ]

        self.rendering_root[1] = Div('2.1.1')

        widget2 = self.rendering_root.nodes[2]

        widget2.nodes = [
            Div('3.1.1'),
            Div('3.2.1'),
            Div('3.3.1'),
        ]

        self.rendering_root[3] = Div('4.1.1')

    @client_version(1)
    def step_56(self):
        self.set_step_label(56, 'Legacy Widgets: Insert Nodes')

        widget1 = self.rendering_root[0]
        widget1.nodes.insert(2, Div('1.2.1.1'))

        self.rendering_root.insert(2, Div('2.2'))

        widget2 = self.rendering_root[3]
        widget2.nodes.insert(2, Div('3.2.1.1'))

    @client_version(1)
    def step_57(self):
        self.set_step_label(57, 'Legacy Widgets: Remove Nodes')

        widget1 = self.rendering_root[0]
        widget1.nodes.pop(2)

        widget2 = self.rendering_root[3]
        widget2.nodes.pop(2)
