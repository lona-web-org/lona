from lona.html.parsing import html_string_to_node_list
from lona.html.text_node import TextNode
from lona.html.widget import Widget


class HTML(Widget):
    def __init__(self, *nodes):
        self.nodes = []

        for node in nodes:

            # strings
            if isinstance(node, str):

                # escaped text
                if node.startswith('\\'):
                    self.nodes.append(TextNode(node[1:]))

                # html string
                elif '<' in node or '>' in node:
                    if len(nodes) > 1:
                        self.nodes.append(HTML(node))

                    else:
                        self.nodes = html_string_to_node_list(node)

                else:
                    self.nodes.append(TextNode(node))

            # lona nodes
            else:
                self.nodes.append(node)

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
