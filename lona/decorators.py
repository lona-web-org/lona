def multiuser(function=None):
    def decorator(function):
        function.multiuser = True

        return function

    if function:
        return decorator(function)

    return decorator
