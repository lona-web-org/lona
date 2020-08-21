def continue_in_background(function=None):
    def decorator(function):
        function.continue_in_background = True

        return function

    if function:
        return decorator(function)

    return decorator


def multiuser(function=None):
    def decorator(function):
        function.multiuser = True

        return function

    if function:
        return decorator(function)

    return decorator
