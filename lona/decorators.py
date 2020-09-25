def multi_user(function=None):
    def decorator(function):
        function.multi_user = True

        return function

    if function:
        return decorator(function)

    return decorator
