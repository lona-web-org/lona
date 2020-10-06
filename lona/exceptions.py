class StopReason(Exception):
    pass


class UserAbort(StopReason):
    pass


class ServerStop(StopReason):
    pass
