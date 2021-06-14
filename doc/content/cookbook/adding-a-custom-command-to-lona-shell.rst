

Adding A Custom Command To Lona Shell
=====================================


.. code-block:: python

    # commands/hello_world.py

    from rlpython.utils.argument_parser import ReplArgumentParser


    class HelloWorldCommand:
        """
        prints "Hello World"
        """

        NAME = 'hello_world'

        def __init__(self, repl):
            self.repl = repl

        def complete(self, text, state, line_buffer):
            # tab completion (optional)

            raw_candidates = ['Hello', 'World']
            candidates = []

            for candidate in raw_candidates:
                if candidate.startswith(text)
                    candidates.append(candidate)

            candidates.append(None)

            return candidates[state]

        def run(self, argv):
            # getting a reference to the currently running lona server
            server = self.repl.locals['server']

            # parse command line
            argument_parser = ReplArgumentParser(
                repl=self.repl,
                prog='hello_world',
            )

            argument_parser.add_argument('--silent')

            arguments = argument_parser.parse_args(argv[1:])

            # print hello world
            if not arguments.silent:
                self.repl.write('Hello World\n')

.. code-block:: python

    # settings.py

    COMMANDS = [
        'commands/hello_world.py::HelloWorldCommand',
    ]
