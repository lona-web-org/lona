import numpy

from lona.html import NumberInput, Button, CLICK, Span, HTML, Div, H1
from lona import LonaView, LonaApp

app = LonaApp(__file__)

app.add_static_file('lona/style.css', """
    body {
        font-family: sans-serif;
    }

    input[type=number] {
        width: 4em;
    }

    button#resize {
        margin-left: 0.5em;
    }

    button#reset {
        margin-left: 5em;
    }

    div#board {
        margin-top: 1em;
    }

    div.row {
        height: 10px;
    }

    div.cell {
        float: left;
        width: 10px;
        height: 10px;
        background-color: black;
    }

    div.cell:hover {
        background-color: grey;
    }

    div.cell.alive {
        background-color: white;
    }
""")


class Cell(Div):
    CLASS_LIST = ['cell']
    EVENTS = [CLICK]

    @property
    def alive(self):
        return 'alive' in self.class_list

    @alive.setter
    def alive(self, new_value):
        if new_value:
            self.class_list.add('alive')

        else:
            self.class_list.remove('alive')


@app.route('/')
class GameOfLiveView(LonaView):

    # controls ################################################################
    def handle_resize(self, input_event):
        if self.running:
            return

        self.setup_board()

    def handle_reset(self, input_event):
        if self.running:
            return

        self.data = self.generate_data()
        self.write_data_to_board(self.data)

    def handle_stop(self, input_event):
        self.running = False

    def handle_cell_click(self, input_event):
        if self.running:
            return

        with self.html.lock:
            x, y = input_event.node.attributes['data-gol-id'].split(':')
            x = int(x)
            y = int(y)

            # set data
            self.data[y][x] = not self.data[y][x]

            # set cell
            cell = self.board.nodes[y][x]
            cell.alive = not cell.alive

    def disable_controls(self):
        with self.html.lock:
            self.html.query_selector('#width').disabled = True
            self.html.query_selector('#height').disabled = True
            self.html.query_selector('#resize').disabled = True
            self.html.query_selector('#reset').disabled = True
            self.html.query_selector('#start').disabled = True
            self.html.query_selector('#stop').disabled = False

    def enable_controls(self):
        with self.html.lock:
            self.html.query_selector('#width').disabled = False
            self.html.query_selector('#height').disabled = False
            self.html.query_selector('#resize').disabled = False
            self.html.query_selector('#reset').disabled = False
            self.html.query_selector('#start').disabled = False
            self.html.query_selector('#stop').disabled = True

    # game logic ##############################################################
    def generate_data(self):
        return numpy.zeros((self.height, self.width))

    def generate_next_generation(self):
        current_generation = self.data
        next_generation = self.generate_data()

        for row, col in numpy.ndindex(current_generation.shape):
            # cell is alive
            cell_is_alive = current_generation[row, col] == 1

            # find neighbors
            neighbors = numpy.sum(current_generation[row-1:row+2, col-1:col+2])
            neighbors = neighbors - current_generation[row, col]

            # set cell
            if cell_is_alive and neighbors < 2 or neighbors > 3:
                next_generation[row, col] = 0

            elif cell_is_alive and 2 <= neighbors <= 3:
                next_generation[row, col] = 1

            elif not cell_is_alive and neighbors == 3:
                next_generation[row, col] = 1

        return next_generation

    def write_data_to_board(self, data):
        for row, col in numpy.ndindex(data.shape):
            self.board.nodes[row][col].alive = data[row, col] > 0

    def setup_board(self):
        with self.html.lock:
            try:
                self.width = int(self.html.query_selector('#width').value)
                self.height = int(self.html.query_selector('#height').value)

            except ValueError:
                return

            # setup data
            self.data = self.generate_data()

            # setup board
            self.board.nodes.clear()

            for y in range(self.height):
                row = Div(_class='row')
                self.board.append(row)

                for x in range(self.width):
                    cell = Cell(
                        handle_click=self.handle_cell_click,
                        data_gol_id=f'{x}:{y}',
                    )

                    row.append(cell)

    # request handling ########################################################
    def handle_request(self, request):
        self.running = False

        # setup html
        self.html = HTML(
            H1('Game Of Life'),

            # controls
            'Width: ',
            NumberInput(
                _id='width',
                value=60,
            ),

            ' Height: ',
            NumberInput(
                _id='height',
                value=40,
            ),

            Button(
                'Resize',
                _id='resize',
                handle_click=self.handle_resize,
            ),

            Button(
                'Reset',
                _id='reset',
                handle_click=self.handle_reset,
            ),

            Button(
                'Start',
                _id='start',
            ),

            Button(
                'Stop',
                _id='stop',
                disabled=True,
                handle_click=self.handle_stop,
            ),

            # generation counter
            Div('Generation: ', Span('0', _id='generation')),

            # board
            Div(_id='board'),
        )

        # setup board
        self.board = self.html.query_selector('#board')
        self.generation = self.html.query_selector('#generation')

        self.setup_board()

        # main loop
        while True:
            self.show(self.html)

            # wait for 'Start' to be pressed
            self.await_click(self.html.query_selector('#start'))

            # reset generation counter
            generation = 0

            self.generation.set_text('0')
            self.show(self.html)

            # start
            self.running = True
            self.disable_controls()

            while self.running:

                # calculate next generation
                next_generation = self.generate_next_generation()

                # stop when the board stops evolving
                if numpy.array_equal(self.data, next_generation):
                    self.running = False

                    break

                self.write_data_to_board(next_generation)
                self.data = next_generation

                # increase generation counter
                generation += 1
                self.generation.set_text(str(generation))

                self.show()
                self.sleep(0.1)

            self.enable_controls()


if __name__ == '__main__':
    app.run(port=8080)
