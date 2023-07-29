import warnings as original_warnings
import inspect


class ExtendedWarn:
    warn = original_warnings.warn

    def __call__(
        self, message, category=None, stacklevel=1, source=None, callee=None,
    ):
        # Check if message is already a Warning object
        if isinstance(message, Warning):
            category = message.__class__
        if callee:
            assert stacklevel == 1
            if category is not None:
                filename = callee.__func__.__code__.co_filename
                lineno = callee.__func__.__code__.co_firstlineno
                message = ('callee', message, filename, lineno, category)
        else:
            stacklevel += 1
        self.warn(message, category, stacklevel, source)  # NOQA: G010


warn = ExtendedWarn()
original_warnings.warn = warn  # type: ignore

_original_formatwarning = original_warnings.formatwarning


def _formatwarning_with_callee(message, category, filename, lineno, line):
    try:
        if (
            not isinstance(message, str)
            and isinstance(message.args[0], tuple)
            and len(message.args[0]) == 5
            and message.args[0][0] == 'callee'
        ):
            _, message, filename, lineno, category = message.args[0]
    except Exception:
        # show original e.g. when message is not a string,
        # but has not .args attribute
        pass
    return _original_formatwarning(message, category, filename, lineno, line)


original_warnings.formatwarning = _formatwarning_with_callee  # type: ignore


class Lona_2_0_DeprecationWarning(PendingDeprecationWarning):
    pass


original_warnings.simplefilter(
    'once', category=Lona_2_0_DeprecationWarning,
)


class DictResponseDeprecationWarning(Lona_2_0_DeprecationWarning):
    pass


class DaemonizeDeprecationWarning(Lona_2_0_DeprecationWarning):
    pass


def remove_2_0(msg=None, _class=False):
    if msg is None:
        if _class:
            msg = 'class '
            msg += inspect.stack()[1].frame.f_locals['self'].__class__.__name__
        else:
            msg = inspect.stack()[1].function + '()'
    original_warnings.warn(  # NOQA: G010
        msg + ' will be removed in 2.0',  # NOQA: G003
        Lona_2_0_DeprecationWarning,
        stacklevel=2,
    )
