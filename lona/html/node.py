from textwrap import indent

from lona.html.attribute_dict import AttributeDict, StyleDict
from lona.html.attribute_list import IDList, ClassList
from lona.html.node_event_list import NodeEventList
from lona.html.abstract_node import AbstractNode
from lona.html.node_list import NodeList
from lona.protocol import NODE_TYPE


class Node(AbstractNode):
    TAG_NAME = 'html'
    SELF_CLOSING_TAG = False
    ID_LIST = []
    CLASS_LIST = []
    STYLE = {}
    ATTRIBUTES = {}
    EVENTS = []

    def __init__(self, *args, tag_name=None, self_closing_tag=None, **kwargs):
        self._id_list = IDList(self, self.ID_LIST)
        self._class_list = ClassList(self, self.CLASS_LIST)
        self._style = StyleDict(self, self.STYLE)
        self._attributes = AttributeDict(self, self.ATTRIBUTES)
        self._nodes = NodeList(self)
        self._events = NodeEventList(self, self.EVENTS)

        # tag overrides
        self.tag_name = tag_name or self.TAG_NAME

        if self_closing_tag is None:
            self.self_closing_tag = self.SELF_CLOSING_TAG

        else:
            self.self_closing_tag = self_closing_tag

        # args (nodes)
        for arg in args:
            self.append(arg)

        # kwargs (attributes)
        for name, value in kwargs.items():

            # remove underscores from attributes
            # this makes kwargs like '_class' possible to prevent clashes
            # with python grammar
            if '_' in name:
                name = name.replace('_', '-')

                if name.startswith('-'):
                    name = name[1:]

            # lona classes
            if name in ('ignore'):
                setattr(self, name, value)

            # patchable attributes
            elif name == 'id':
                if not isinstance(value, (str, list)):
                    raise ValueError('id has to be string or list of srings')  # NOQA

                if isinstance(value, str):
                    value = value.split(' ')

                self._id_list.extend(value)

            elif name == 'class':
                if not isinstance(value, (str, list)):
                    raise ValueError('class has to be string or list of srings')  # NOQA

                if isinstance(value, str):
                    value = value.split(' ')

                self._class_list.extend(value)

            elif name == 'style':
                if not isinstance(value, dict):
                    raise ValueError('style has to be dict')

                self._style.update(value)

            elif name == 'attributes':
                if not isinstance(value, dict):
                    raise ValueError('attributes has to be dict')

                self._attributes.update(value)

            elif name == 'events':
                if not isinstance(value, list):
                    raise ValueError('events have to be list')

                self._events.extend(value)

            elif name == 'nodes':
                if not isinstance(value, list):
                    value = [value]

                self._nodes._reset(value)

            # misc attributes
            else:
                self._attributes[name] = value

    # node attributes  ########################################################
    # id_list
    @property
    def id_list(self):
        return self._id_list

    @id_list.setter
    def id_list(self, value):
        self._id_list._reset(value)

    # class_list
    @property
    def class_list(self):
        return self._class_list

    @class_list.setter
    def class_list(self, value):
        self._class_list._reset(value)

    # style
    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style._reset(value)

    # attributes
    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, value):
        self._attributes._reset(value)

    # events
    @property
    def events(self):
        return self._events

    @events.setter
    def events(self, value):
        self._events._reset(value)

    # nodes
    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, value):
        self._nodes._reset(value)

    # lona attribute helper ###################################################
    def has_class(self, class_name):
        return class_name in self._class_list

    def has_id(self, id_name):
        return id_name in self._id_list

    # lona attributes #########################################################
    @property
    def ignore(self):
        return 'data-lona-ignore' in self._attributes

    @ignore.setter
    def ignore(self, value):
        if value:
            self._attributes['data-lona-ignore'] = 'True'

        else:
            with self.lock:
                if 'data-lona-ignore' in self._attributes:
                    del self._attributes['data-lona-ignore']

    # serialisation ###########################################################
    def _has_patches(self):
        return any([
            self._id_list._has_patches(),
            self._class_list._has_patches(),
            self._style._has_patches(),
            self._attributes._has_patches(),
            self._nodes._has_patches(),
        ])

    def _get_patches(self):
        return [
            *self._id_list._get_patches(),
            *self._class_list._get_patches(),
            *self._style._get_patches(),
            *self._attributes._get_patches(),
            *self._nodes._get_patches(),
        ]

    def _clear_patches(self):
        self._id_list._clear_patches()
        self._class_list._clear_patches()
        self._style._clear_patches()
        self._attributes._clear_patches()
        self._nodes._clear_patches()

    def _serialize(self):
        return [
            NODE_TYPE.NODE,
            self.id,
            self.tag_name,
            self._id_list._serialize(),
            self._class_list._serialize(),
            self._style._serialize(),
            self._attributes._serialize(),
            self._nodes._serialize(),
        ]

    # node list helper ########################################################
    def insert(self, index, node):
        self._nodes.insert(index, node)

    def append(self, node):
        self._nodes.append(node)

    def remove(self, node=None):
        if not node:
            if not self._parent:
                raise RuntimeError('node has no parent node')

            self._parent.remove(self)

            return

        self._nodes.remove(node)

    def pop(self, index):
        return self._nodes.pop(index)

    def clear(self):
        self._nodes.clear()

    def __getitem__(self, index):
        return self._nodes[index]

    def __setitem__(self, index, value):
        self._nodes[index] = value

    def __iter__(self):
        return self._nodes.__iter__()

    def __len__(self):
        return self._nodes.__len__()

    def __bool__(self):
        return True

    # string representation ###################################################
    def __str__(self, node_string=None, skip_value=False):
        with self.lock:
            # opening tag
            string = '<{} data-lona-node-id="{}"'.format(
                self.tag_name,
                self.id,
            )

            if self.id_list:
                string += ' id="{}"'.format(str(self.id_list))

            if self.class_list:
                string += ' class="{}"'.format(str(self.class_list))

            if self.style:
                string += ' style="{}"'.format(
                    self.style.to_sub_attribute_string())

            if self.attributes:
                string += ' '

                string += self.attributes.to_attribute_string(
                    skip_value=skip_value,
                )

            if self.self_closing_tag:
                string += ' />'

            else:
                string += '>'

            # nodes
            if node_string:
                string += '\n{}\n'.format(
                    indent(node_string, '  '),
                )

            elif self.nodes:
                string += '\n'
                string += indent(str(self.nodes), '  ')
                string += '\n'

            # closing tag
            if not self.self_closing_tag:
                string += '</{}>'.format(self.tag_name)

            return string

    def __repr__(self):
        return self.__str__()

    # comparrison #############################################################
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False

        # campare attributes
        return (
            self.tag_name,
            self.self_closing_tag,
            self._id_list,
            self._class_list,
            self._style,
            self._attributes,
            self._nodes,
        ) == (
            other.tag_name,
            other.self_closing_tag,
            other._id_list,
            other._class_list,
            other._style,
            other._attributes,
            other._nodes,
        )

    # HTML helper #############################################################
    def set_text(self, text):
        self.nodes = [str(text)]

    def get_text(self):
        with self.lock:
            text = []

            for node in self.nodes:
                text.append(node.get_text())

            text = ' '.join(text)

            # strip starting and ending whitespaces but preserve \n
            # this is important for nodes like <pre> which are newline aware
            while text.startswith('\t') or text.startswith(' '):
                text = text[1:]

            while text.endswith('\t') or text.endswith(' '):
                text = text[:1]

            return text

    def hide(self):
        self.style['display'] = 'none'

    def show(self):
        with self.lock:
            if 'display' in self.style and self.style['display'] == 'none':
                del self.style['display']
