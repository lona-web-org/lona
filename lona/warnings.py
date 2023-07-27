import warnings as org_warnings


class ExtendedWarn:
    warn = org_warnings.warn

    def __call__(
        self, message, category=None, stacklevel=1, source=None, callee=None
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
        self.warn(message, category, stacklevel, source)  # NOQA


org_warnings.warn = warn = ExtendedWarn()

_org_formatwarning = org_warnings.formatwarning


def my_formatwarning(message, category, filename, lineno, line):
    if (
        isinstance(message.args[0], tuple)
        and len(message.args[0]) == 5
        and message.args[0][0] == 'callee'
    ):
        try:
            _, message, filename, lineno, category = message.args[0]
        except ValueError:  # in case there was no tuple provided
            pass
            raise
    return _org_formatwarning(message, category, filename, lineno, line)


org_warnings.formatwarning = my_formatwarning


class DictResponseDeprecationWarning(PendingDeprecationWarning):
    pass


org_warnings.simplefilter(
    'once', category=DictResponseDeprecationWarning,
)
