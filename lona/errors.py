class ForbiddenError(Exception):
    pass


class ClientError(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message

        super().__init__(*args, **kwargs)
