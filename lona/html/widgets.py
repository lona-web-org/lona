from lona.html.widget import Widget


class HTML(Widget):
    def __init__(self, *nodes):
        self.nodes = [*nodes]

    def insert(self, *args, **kwargs):
        return self.nodes.insert(*args, **kwargs)

    def append(self, *args, **kwargs):
        return self.nodes.append(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self.nodes.remove(*args, **kwargs)

    def clear(self, *args, **kwargs):
        return self.nodes.clear(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self.nodes.__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.nodes.__setitem__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self.nodes.__iter__(*args, **kwargs)

    def __bool__(self, *args, **kwargs):
        return self.nodes.__bool__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self.nodes.__len__(*args, **kwargs)
