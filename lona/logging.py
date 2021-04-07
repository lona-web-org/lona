from traceback import format_exception
from textwrap import indent
import threading
import datetime
import logging
import socket


class LogFilter(logging.Filter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.excluded = []
        self.included = []

    def include(self, logger_name):
        self.included.append(logger_name)

    def exclude(self, logger_name):
        self.excluded.append(logger_name)

    def filter(self, record):
        # filter exceptions that lona.command_line.run_server.run_server
        # handles it self
        if record.exc_info:

            # OSErrors
            if(isinstance(record.exc_info[1], OSError) and
               record.exc_info[1].errno in (13, 98)):

                return False

            # socket.gaierror
            if(isinstance(record.exc_info[1], socket.gaierror) and
               record.exc_info[1].errno in (-2, )):

                return False

        if record.name in self.excluded:
            return False

        if self.included and record.name not in self.included:
            return False

        return True


class LogFormatter(logging.Formatter):
    def format(self, record):
        current_thread_name = threading.current_thread().name

        # format record string
        time_stamp = datetime.datetime.fromtimestamp(record.created)
        time_stamp_str = time_stamp.strftime('%H:%M:%S.%f')

        record_string = '{}{} {}{} {} {} {}'.format(
            current_thread_name,
            (30 - len(current_thread_name)) * ' ',

            record.levelname,
            (8 - len(record.levelname)) * ' ',

            time_stamp_str,
            record.name,
            record.getMessage(),
        )

        # format exc_info
        if record.exc_info:
            record_string = '{}\n{}'.format(
                record_string,
                indent(
                    ''.join(format_exception(*record.exc_info))[:-1],
                    prefix='  ',
                ),
            )

        # colors
        RED = '31'
        YELLOW = '33'
        WHITE = '37'
        GREEN = '32'
        BACKGROUND_RED = '41'

        BRIGHT = '1'

        if record.levelname == 'DEBUG':
            style = ''
            background = ''
            color = GREEN

        elif record.levelname == 'INFO':
            style = ''
            background = ''
            color = WHITE

        elif record.levelname == 'WARNING':
            style = ''
            background = ''
            color = YELLOW

        elif record.levelname == 'ERROR':
            style = BRIGHT
            background = ''
            color = RED

        elif record.levelname == 'CRITICAL':
            style = BRIGHT
            background = BACKGROUND_RED
            color = WHITE

        if style:
            color = ';{}'.format(color)

        if background and color:
            background = ';{}'.format(background)

        return '\033[{}{}{}m{}\033[00m'.format(
            style,
            color,
            background,
            record_string,
        )
