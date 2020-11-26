class Symbol:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __eq__(self, other):
        return other == self.value

    def __repr__(self):
        return self.name
