from __future__ import annotations

from collections.abc import Iterable
from textwrap import indent

from lona.html.attribute_dict import AttributeDict, StyleDict
from lona.html.attribute_list import ClassList, IDList
from lona.html.node_event_list import NodeEventList
from lona.events import ChangeEventType, EventType
from lona.html.abstract_node import AbstractNode
from lona.html.widget_data import WidgetData
from lona.html.node_list import NodeList
from lona.protocol import NODE_TYPE


def parse_style_string(style_string: str) -> dict[str, str]:
    values = {}

    for css_rule in style_string.split(';'):
        if not css_rule.strip():
            continue

        if ':' not in css_rule:
            raise ValueError(f'Invalid style string: {style_string}')

        name, value = css_rule.split(':', 1)

        values[name.strip()] = value.strip()

    return values


class Node(AbstractNode):
    TAG_NAME = 'html'
    SELF_CLOSING_TAG = False
    ID_LIST: list[str] = []
    CLASS_LIST: list[str] = []
    STYLE: dict[str, str] | str = {}
    ATTRIBUTES: dict[str, str] = {}
    EVENTS: list[EventType | ChangeEventType] = []
    WIDGET: str = ''

    def __init__(
            self,
            *args,
            tag_name=None,
            self_closing_tag=None,
            widget='',
            **kwargs,
    ):

        self._id_list = IDList(self, self.ID_LIST)
        self._class_list = ClassList(self, self.CLASS_LIST)
        self._style = StyleDict(self, self.STYLE)
        self._attributes = AttributeDict(self, self.ATTRIBUTES)
        self._nodes = NodeList(self)
        self._events = NodeEventList(self, self.EVENTS)
        self._widget = widget or self.WIDGET
        self._widget_data = WidgetData(widget=self)

        # tag overrides
        self.tag_name = tag_name or self.TAG_NAME

        if self_closing_tag is None:
            self.self_closing_tag = self.SELF_CLOSING_TAG

        else:
            self.self_closing_tag = self_closing_tag

        # args (nodes)
        for arg in args:
            if isinstance(arg, (AbstractNode, str)):
                self.append(arg)

            elif isinstance(arg, Iterable):
                for node in list(arg):
                    self.append(node)

            else:
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
            if name == 'ignore':
                setattr(self, name, value)

            # patchable attributes
            elif name == 'id':
                if not isinstance(value, (str, list)):
                    raise ValueError(
                        'id has to be string or list of strings',
                    )

                if isinstance(value, str):
                    value = value.split(' ')

                self._id_list.extend(value)

            elif name == 'class':
                if not isinstance(value, (str, list)):
                    raise ValueError(
                        'class has to be string or list of strings',
                    )

                if isinstance(value, str):
                    value = value.split(' ')

                self._class_list.extend(value)

            elif name == 'style':
                if not isinstance(value, (dict, str)):
                    raise ValueError('style has to be dict or string')

                if isinstance(value, str):
                    value = parse_style_string(value)

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

            elif name == 'handle-change':  # '_' was replaced to '-' above
                if not callable(value):
                    raise TypeError('handle_change has to be a function')

                self.handle_change = value

            elif name == 'handle-click':  # '_' was replaced to '-' above
                if not callable(value):
                    raise TypeError('handle_click has to be a function')

                self.handle_click = value

            elif name == 'handle-focus':  # '_' was replaced to '-' above
                if not callable(value):
                    raise TypeError('handle_focus has to be a function')

                self.handle_focus = value

            elif name == 'handle-blur':  # '_' was replaced to '-' above
                if not callable(value):
                    raise TypeError('handle_blur has to be a function')

                self.handle_blur = value

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

    # widget_data
    @property
    def widget_data(self):
        return self._widget_data

    @widget_data.setter
    def widget_data(self, value):
        self._widget_data._reset(value)

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
        if not isinstance(value, bool):
            raise TypeError('ignore is a boolean property')

        if value:
            self._attributes['data-lona-ignore'] = ''

        else:
            del self._attributes['data-lona-ignore']

    # serialization ###########################################################
    def _serialize(self):
        widget_data = None

        if self._widget:
            widget_data = self._widget_data._serialize()

        return [
            NODE_TYPE.NODE,
            self.id,
            self.tag_name,
            self._id_list._serialize(),
            self._class_list._serialize(),
            self._style._serialize(),
            self._attributes._serialize(),
            self._nodes._serialize(),
            self._widget,
            widget_data,
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
            string = f'<{self.tag_name} data-lona-node-id="{self.id}"'

            if self.id_list:
                string += f' id="{self.id_list}"'

            if self.class_list:
                string += f' class="{self.class_list}"'

            if self.style:
                string += f' style="{self.style.to_sub_attribute_string()}"'

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
                string += '\n'
                string += indent(node_string, '  ')
                string += '\n'

            elif self.nodes:
                string += '\n'
                string += indent(str(self.nodes), '  ')
                string += '\n'

            # closing tag
            if not self.self_closing_tag:
                string += f'</{self.tag_name}>'

            return string

    def __repr__(self):
        return self.__str__()

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
