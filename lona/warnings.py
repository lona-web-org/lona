import warnings as orginal_warnings


class ExtendedWarn:
    warn = orginal_warnings.warn

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
orginal_warnings.warn = warn  # type: ignore

_original_formatwarning = orginal_warnings.formatwarning


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


orginal_warnings.formatwarning = _formatwarning_with_callee  # type: ignore


class DictResponseDeprecationWarning(PendingDeprecationWarning):
    pass


orginal_warnings.simplefilter(
    'once', category=DictResponseDeprecationWarning,
)
