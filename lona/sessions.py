class AnonymousUser:
    def __repr__(self):
        return '<AnonymousUser()>'

    def __eq__(self, other):
        return isinstance(other, AnonymousUser)
