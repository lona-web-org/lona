from rlpython.utils.argument_parser import ReplArgumentParser


class LonaMiddlewaresCommand:
    """
    List all middleware hooks
    """

    NAME = 'lona_middlewares'

    def __init__(self, repl):
        self.repl = repl

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(
            repl=self.repl,
            prog='lona_middlewares',
            description=self.__doc__,
        )

        argument_parser.parse_args(argv[1:])

        server = self.repl.locals['server']
        middleware_controller = server.middleware_controller

        # list middlewares
        hook_names = [
            'on_startup',
            'on_shutdown',
            'handle_connection',
            'handle_websocket_message',
            'handle_request',
        ]

        for hook_name in hook_names:
            self.repl.write('{}\n'.format(hook_name))

            for middleware, hook in middleware_controller.hooks[hook_name]:
                self.repl.write(
                    '    {}.{}\n'.format(
                        middleware.__module__,
                        middleware.__class__.__name__),
                )

            self.repl.write('\n')
