import sys
import os


def terminal_supports_colors():
    return (
        # check if stdout is a tty
        hasattr(sys.stdout, 'isatty') and
        sys.stdout.isatty()
    ) and (
        # Windows checks
        sys.platform != 'win32' or
        'ANSICON' in os.environ or

        # Windows Terminal supports VT codes
        'WT_SESSION' in os.environ or

        # Microsoft Visual Studio Code's built-in terminal supports colors
        os.environ.get('TERM_PROGRAM') == 'vscode'
    )


def colors_are_enabled():
    # https://no-color.org/

    return 'NO_COLOR' not in os.environ
