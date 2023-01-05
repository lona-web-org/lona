from lona.html import Select, Button, Span, HTML, Div, H3, H2
from lona.static_files import Script
from lona._json import dumps
from lona import View


class WidgetDataTestComponent(Div):
    WIDGET = 'WidgetDataTestWidget'

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


class RenderingTestView(View):
    STATIC_FILES = [
        Script(name='RenderingTestWidgets', path='rendering-test-widgets.js'),
    ]

    def handle_mode_change(self, input_event):
        select = input_event.node

        with self.html.lock:
            self.start.disabled = select.value != 'auto'
            self.stop.disabled = select.value != 'auto'
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

        self.rendering_step_label = H3(
            'Step ',
            Span(_id='current'),
            '/',
            Span(_id='total'),
            ': ',
            Span(_id='label'),
            _id='step-label',
        )

        self.rendering_root = Div(_id='rendering-root')

        self.html = HTML(
            H2('Rendering Test'),
            Div(
                self.mode,
                self.start,
                self.stop,
                self.next_step,
                self.reset,
            ),
            self.rendering_step_label,
            self.rendering_root,
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
                    self.sleep(0.5)

    # rendering steps #########################################################
    def reset_rendering_steps(self):
        with self.html.lock:
            self.running = False
            self.steps = self.get_rendering_steps()
            self.current_step_index = 0
            self.rendering_root.clear()

            self.set_step_label(0, 'Not started')

    def get_rendering_steps(self):
        steps = []

        for attribute_name in dir(self):
            if not attribute_name.startswith('step_'):
                continue

            steps.append(getattr(self, attribute_name))

        return steps

    def run_next_step(self):
        step = self.steps[self.current_step_index]

        step()

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
    def step_01(self):
        with self.html.lock:
            self.set_step_label(1, 'Clear Nodes')

            self.rendering_root.clear()

    def step_02(self):
        with self.html.lock:
            self.set_step_label(2, 'Append Nodes')

            self.rendering_root.append(Div('first div'))
            self.rendering_root.append(Div('second div'))

    def step_03(self):
        with self.html.lock:
            self.set_step_label(3, 'Set Node')

            self.rendering_root[0] = Div('set div')

    def step_04(self):
        with self.html.lock:
            self.set_step_label(4, 'Reset Nodes')

            self.rendering_root.nodes = [
                Div('reset div1'),
                Div('reset div2'),
            ]

    def step_05(self):
        with self.html.lock:
            self.set_step_label(5, 'Insert Node')

            self.rendering_root.nodes.insert(1, Div('inserted div'))

    def step_06(self):
        with self.html.lock:
            self.set_step_label(6, 'Remove Node')

            self.rendering_root.nodes[1].remove()

    # id_list tests
    def step_07(self):
        with self.html.lock:
            self.set_step_label(7, 'Set id')

            self.rendering_root.nodes = [
                Div(_id='foo bar'),
            ]

    def step_08(self):
        with self.html.lock:
            self.set_step_label(8, 'Add id')

            self.rendering_root.nodes[0].id_list.add('baz')

    def step_09(self):
        with self.html.lock:
            self.set_step_label(9, 'Remove id')

            self.rendering_root.nodes[0].id_list.remove('bar')

    def step_10(self):
        with self.html.lock:
            self.set_step_label(10, 'Reset id')

            self.rendering_root.nodes[0].id_list = ['foo1', 'bar1']

    def step_11(self):
        with self.html.lock:
            self.set_step_label(11, 'Clear id')

            self.rendering_root.nodes[0].id_list.clear()

    # class_list tests
    def step_12(self):
        with self.html.lock:
            self.set_step_label(12, 'Set class')

            self.rendering_root.nodes = [
                Div(_class='foo bar'),
            ]

    def step_13(self):
        with self.html.lock:
            self.set_step_label(13, 'Add class')

            self.rendering_root.nodes[0].class_list.add('baz')

    def step_14(self):
        with self.html.lock:
            self.set_step_label(14, 'Remove class')

            self.rendering_root.nodes[0].class_list.remove('bar')

    def step_15(self):
        with self.html.lock:
            self.set_step_label(15, 'Reset class')

            self.rendering_root.nodes[0].class_list = ['foo1', 'bar1']

    def step_16(self):
        with self.html.lock:
            self.set_step_label(16, 'Clear class')

            self.rendering_root.nodes[0].class_list.clear()

    # attribute tests
    def step_17(self):
        with self.html.lock:
            self.set_step_label(17, 'Set attributes')

            self.rendering_root.nodes = [
                Div(foo='foo', bar='bar'),
            ]

    def step_18(self):
        with self.html.lock:
            self.set_step_label(18, 'Add attribute')

            self.rendering_root.nodes[0].attributes['baz'] = 'baz'

    def step_19(self):
        with self.html.lock:
            self.set_step_label(19, 'Remove attribute')

            del self.rendering_root.nodes[0].attributes['foo']

    def step_20(self):
        with self.html.lock:
            self.set_step_label(20, 'Reset attributes')

            self.rendering_root.nodes[0].attributes = {
                'foo1': 'bar1',
                'bar1': 'foo1',
            }

    def step_21(self):
        with self.html.lock:
            self.set_step_label(21, 'Clear attributes')

            self.rendering_root.nodes[0].attributes.clear()

    # style tests
    def step_22(self):
        with self.html.lock:
            self.set_step_label(22, 'Set style')

            self.rendering_root.nodes = [
                Div(_style='display: none; position: absolute;'),
            ]

    def step_23(self):
        with self.html.lock:
            self.set_step_label(23, 'Add style')

            self.rendering_root.nodes[0].style['z-index'] = '1'

    def step_24(self):
        with self.html.lock:
            self.set_step_label(24, 'Remove style')

            del self.rendering_root.nodes[0].style['display']

    def step_25(self):
        with self.html.lock:
            self.set_step_label(25, 'Reset style')

            self.rendering_root.nodes[0].style = {
                'position': 'relative',
            }

    def step_26(self):
        with self.html.lock:
            self.set_step_label(26, 'Clear style')

            self.rendering_root.nodes[0].style.clear()

    # widget data tests
    def step_27(self):
        with self.html.lock:
            self.set_step_label(27, 'Widget Data: list: setup')

            self.rendering_root.nodes = [
                WidgetDataTestComponent(
                    initial_state={'list': []},
                ),
            ]

    def step_28(self):
        with self.html.lock:
            self.set_step_label(28, 'Widget Data: list: append')

            component = self.rendering_root.nodes[0]

            component.widget_data['list'].append(1)
            component.widget_data['list'].append(2)
            component.widget_data['list'].append(3)
            component.update_state()

    def step_29(self):
        with self.html.lock:
            self.set_step_label(29, 'Widget Data: list: remove')

            component = self.rendering_root.nodes[0]

            component.widget_data['list'].remove(2)
            component.update_state()

    def step_30(self):
        with self.html.lock:
            self.set_step_label(30, 'Widget Data: list: insert')

            component = self.rendering_root.nodes[0]

            component.widget_data['list'].insert(0, 0)
            component.update_state()

    def step_31(self):
        with self.html.lock:
            self.set_step_label(31, 'Widget Data: list: clear')

            component = self.rendering_root.nodes[0]

            component.widget_data['list'].clear()
            component.update_state()

    def step_32(self):
        with self.html.lock:
            self.set_step_label(32, 'Widget Data: list: reset')

            component = self.rendering_root.nodes[0]

            component.widget_data['list'] = [5, 4, 3, 2, 1]
            component.update_state()

    def step_33(self):
        with self.html.lock:
            self.set_step_label(33, 'Widget Data: dict: setup')

            component = self.rendering_root.nodes[0]

            component.widget_data = {'dict': {}}
            component.update_state()

    def step_34(self):
        with self.html.lock:
            self.set_step_label(34, 'Widget Data: dict: set')

            component = self.rendering_root.nodes[0]

            component.widget_data['dict'][1] = 1
            component.widget_data['dict'][2] = 2
            component.widget_data['dict'][3] = 3
            component.update_state()

    def step_35(self):
        with self.html.lock:
            self.set_step_label(35, 'Widget Data: dict: del')

            component = self.rendering_root.nodes[0]

            del component.widget_data['dict'][2]
            component.update_state()

    def step_36(self):
        with self.html.lock:
            self.set_step_label(36, 'Widget Data: dict: pop')

            component = self.rendering_root.nodes[0]

            component.widget_data['dict'].pop(3)
            component.update_state()

    def step_37(self):
        with self.html.lock:
            self.set_step_label(37, 'Widget Data: dict: clear')

            component = self.rendering_root.nodes[0]

            component.widget_data['dict'].clear()
            component.update_state()

    def step_38(self):
        with self.html.lock:
            self.set_step_label(38, 'Widget Data: dict: reset')

            component = self.rendering_root.nodes[0]

            component.widget_data['dict'] = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
            component.update_state()
