from traceback import format_exception
from textwrap import indent
import threading
import datetime
import logging
import socket
import os

from lona.command_line.terminal import (
    terminal_supports_colors,
    colors_are_enabled,
)

try:
    # syslog is only on unix based systems available
    import syslog

    SYSLOG_IS_AVAILABLE = True

except ImportError:
    SYSLOG_IS_AVAILABLE = False


def journald_is_running():
    return 'JOURNAL_STREAM' in os.environ and 'TERM' not in os.environ


def get_syslog_priority(levelno):
    if levelno <= logging.DEBUG:
        return syslog.LOG_DEBUG

    elif levelno <= logging.INFO:
        return syslog.LOG_INFO

    elif levelno <= logging.WARNING:
        return syslog.LOG_WARNING

    elif levelno <= logging.ERROR:
        return syslog.LOG_ERR

    elif levelno <= logging.CRITICAL:
        return syslog.LOG_CRIT

    return syslog.LOG_ALERT


class LogFilter(logging.Filter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.excluded = []
        self.included = []

    def clear(self):
        self.excluded.clear()
        self.included.clear()

    def include(self, logger_name):
        self.included.append(logger_name)

    def exclude(self, logger_name):
        self.excluded.append(logger_name)

    def filter(self, record):
        # filter exceptions that lona.command_line.run_server.run_server
        # handles it self
        if record.exc_info:

            # OSErrors
            if (isinstance(record.exc_info[1], OSError) and
                    record.exc_info[1].errno in (13, 98)):

                return False

            # socket.gaierror
            if (isinstance(record.exc_info[1], socket.gaierror) and
                    record.exc_info[1].errno in (-2, )):

                return False

        if record.name == 'lona':
            # The lona root logger is used by the command line tools
            # to report errors, for example when startup is not possible due
            # an invalid host or port.
            # These errors can't be ignored.

            return True

        if record.name in self.excluded:
            return False

        if self.included and record.name not in self.included:
            return False

        return True


class LogFormatter(logging.Formatter):
    def __init__(self, *args, syslog_priorities=False, **kwargs):
        super().__init__(*args, **kwargs)

        self.syslog_priorities = SYSLOG_IS_AVAILABLE and syslog_priorities

        self.colors_enabled = (
            terminal_supports_colors() and
            colors_are_enabled()
        )

    def format(self, record):
        current_thread_name = threading.current_thread().name

        # format record string
        time_stamp = datetime.datetime.fromtimestamp(record.created)
        time_stamp_str = time_stamp.strftime('%H:%M:%S.%f')

        record_string = '{}{} {}{} {} {} {}'.format(  # NOQA: FS002
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
            record_string = '{}\n{}'.format(  # NOQA: FS002
                record_string,
                indent(
                    ''.join(format_exception(*record.exc_info))[:-1],
                    prefix='  ',
                ),
            )

        # syslog priorities
        if self.syslog_priorities:
            syslog_priority = get_syslog_priority(record.levelno)

            record_string = f'<{syslog_priority}>{record_string}'

        # colors
        if record.levelname == 'INFO' or not self.colors_enabled:
            return record_string

        RED = '31'
        YELLOW = '33'
        WHITE = '37'
        GREEN = '32'
        BACKGROUND_RED = '41'

        BRIGHT = '1'

        style = ''
        background = ''
        color = ''

        if record.levelname == 'DEBUG':
            style = ''
            background = ''
            color = GREEN

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
            color = f';{color}'

        if background and color:
            background = f';{background}'

        return f'\033[{style}{color}{background}m{record_string}\033[00m'


def setup_logging(args):
    # set log level
    if not args.debug_mode:
        log_level = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warn': logging.WARN,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }[args.log_level.lower()]

    else:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)

    # syslog priorities
    if args.syslog_priorities == 'always':
        syslog_priorities = True

    elif args.syslog_priorities == 'no':
        syslog_priorities = False

    elif args.syslog_priorities == 'auto':
        syslog_priorities = journald_is_running()

    # setup log formatting and log filtering
    log_formatter = LogFormatter(syslog_priorities=syslog_priorities)
    log_filter = LogFilter()

    for handler in logging.getLogger().root.handlers:
        handler.setFormatter(log_formatter)
        handler.addFilter(log_filter)

    if args.debug_mode:
        if args.debug_mode == 'messages':
            log_filter.include('lona.server.websockets')

        elif args.debug_mode == 'views':
            log_filter.include('lona.views')

        elif args.debug_mode == 'input-events':
            log_filter.include('lona.input_events')

        elif args.debug_mode == 'view-events':
            log_filter.include('lona.view_events')

    elif args.loggers:
        for logger_name in args.loggers:
            if logger_name.startswith('_'):
                log_filter.exclude(logger_name[1:])

            else:
                if logger_name.startswith('+'):
                    logger_name = logger_name[1:]

                log_filter.include(logger_name)

    return log_formatter, log_filter
