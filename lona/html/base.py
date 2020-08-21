from datetime import datetime
from textwrap import indent
from copy import copy


# basic types #################################################################
class DirtyObject:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.clean()

    def clean(self):
        self._state = self._get_state()
        self._dirty = False

    def _get_state(self):
        pass

    def _check_state(self):
        self._dirty = self._get_state() != self._state

    @property
    def dirty(self):
        return self._dirty

    def _method_wrapper(self, original_method):
        def wrapper(*args, **kwargs):
            value = original_method(*args, **kwargs)
            self._check_state()

            return value

        return wrapper

    def __getattribute__(self, name):
        attribute = super().__getattribute__(name)

        if name.startswith('_'):
            return attribute

        if callable(attribute):
            return self._method_wrapper(attribute)

        return attribute

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        self._check_state()

    def __delitem__(self, key):
        super().__delitem__(key)

        self._check_state()

    def __repr__(self):
        return '{}{}'.format(
            '*' if self.dirty else '',
            super().__repr__()
        )


class DirtyDict(DirtyObject, dict):
    def _get_state(self):
        return dict(self)


class DirtyList(DirtyObject, list):
    def _get_state(self):
        return list(self)


# nodes #######################################################################
class AbstractNode:

    # dirty ###################################################################
    def has_dirty_attributes(self):
        if isinstance(self, Node):
            return any([
                self.id_list.dirty,
                self.class_list.dirty,
                self.attributes.dirty,
                self.style.dirty,
            ])

        return False

    def has_dirty_nodes(self):
        if self.nodes.dirty:
            return True

        for node in self.nodes:
            if isinstance(node, Widget) and node.dirty:
                return True

        return False

    @property
    def dirty(self):
        return self.has_dirty_attributes() or self.has_dirty_nodes()

    def clean(self, recursive=True):

        for attribute in [self._lona_attributes, self.id_list,
                          self.class_list, self.attributes, self.style,
                          self.nodes]:

            if attribute.dirty:
                attribute.clean()

        if not recursive:
            return

        def iter_nodes(node):
            if not isinstance(node, AbstractNode):
                return

            if node is not self and node.dirty:
                node.clean()

            for i in node.nodes:
                iter_nodes(i)

        iter_nodes(self)

    # string methods ##########################################################
    def nodes_to_string(self, node_ids=False, whitespaces=True, debug=None):
        _debug = self.debug

        if debug is not None:
            _debug = debug

        debug = _debug

        node_string = ''

        for node in self.nodes:
            if not node:
                continue

            if isinstance(node, AbstractNode):
                if whitespaces:
                    node_string += '\n'

                node_string += node.to_string(
                    node_ids=node_ids,
                    whitespaces=whitespaces,
                    debug=debug,
                )

            else:
                if whitespaces:
                    node_string += '\n'

                node_string += str(node)

        if node_string and whitespaces:
            node_string = indent(node_string + '\n', self.INDENT_PREFIX)

        return node_string

    def to_string(self, node_ids=False, whitespaces=True, debug=None):
        _debug = self.debug

        if debug is not None:
            _debug = debug

        debug = _debug

        attribute_string = ''

        # dirty
        dirty_string = ''

        if debug and self.dirty:
            dirty_string = '*'

        # lona attributes
        if debug or node_ids:
            attribute_string += ' lona-node-id="{}"'.format(
                self._lona_attributes['id']
            )

        lona_classes = []

        for name in ['clickable', 'changeable']:
            if self._lona_attributes[name]:
                lona_classes.append(name)

        if lona_classes:
            attribute_string += ' lona-classes="{}"'.format(
                ' '.join(lona_classes),
            )

        if self._lona_attributes['widget']:
            attribute_string += ' lona-widget="{}"'.format(
                self._lona_attributes['widget']
            )

        # ids
        id_list = self.id_list

        if id_list:
            attribute_string += ' id="{}"'.format(' '.join(id_list))

        # classes
        if self.class_list:
            attribute_string += ' class="{}"'.format(' '.join(self.class_list))

        for key, value in self.attributes.items():
            if value:
                attribute_string += ' {}="{}"'.format(key, value)

            else:
                attribute_string += ' {}'.format(key)

        # style
        if self.style:
            style_string = ''

            for key, value in self.style.items():
                style_string += '{}: {};'.format(key, value)

            attribute_string += ' style="{}"'.format(style_string)

        # start- and end tag
        start_tag = '<{}{}'.format(self.TAG_NAME,  attribute_string)
        end_tag = ''

        if self.SINGLE_TAG:
            start_tag += ' />'

        else:
            start_tag += '>'
            end_tag = '</{}>'.format(self.TAG_NAME)

        # nodes
        node_string = self.nodes_to_string(
            node_ids=node_ids,
            whitespaces=whitespaces,
            debug=debug,
        )

        return '{}{}{}{}'.format(dirty_string, start_tag, node_string, end_tag)

    def serialize(self):
        return self.to_string(
            node_ids=True,
            whitespaces=False,
            debug=False,
        )

    def serialize_nodes(self):
        return self.nodes_to_string(
            node_ids=True,
            whitespaces=False,
            debug=False,
        )

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    # node tree helper ########################################################
    def get_node(self, node_id):
        if isinstance(node_id, Node):
            node_id = node_id.id

        node_id = str(node_id)
        value = [None, [], ]
        widgets = []

        def iter_nodes(node):
            if isinstance(node, Widget):
                widgets.append(node)

            if isinstance(node, AbstractNode):
                if hasattr(node, 'id') and node.id == node_id:
                    value[0] = node
                    value[1].extend(widgets)

                    return

                if node.nodes:
                    for i in node.nodes:
                        iter_nodes(i)

            if isinstance(node, Widget):
                widgets.pop()

        iter_nodes(self)

        return tuple(value)

    def get_dirty_nodes(self):
        # FIXME: get_dirty_nodes does not recognize empty style attributes

        dirty_nodes = {}

        def check_node(node):
            if not node.dirty:
                return False

            dirty = {}
            dirty_nodes[node.id] = dirty

            # attributes
            if node.has_dirty_attributes():
                dirty['attributes'] = dict(node.attributes)

                if node.id_list:
                    dirty['attributes']['id'] = ' '.join(node.id_list)

                if node.class_list:
                    dirty['attributes']['class'] = ' '.join(node.class_list)

                if node.style:
                    style_string = ''.join(
                        ['{}:{};'.format(k, v) for k, v in node.style.items()])

                    dirty['attributes']['style'] = style_string

            # nodes
            if node.has_dirty_nodes():
                dirty['html'] = node.nodes_to_string(
                    node_ids=True,
                    whitespaces=False,
                )

                return True

        def iter_nodes(node):
            if not isinstance(node, AbstractNode):
                return

            if isinstance(node, Node):
                abort = check_node(node)

                if abort:
                    return

            for child in node.nodes:
                iter_nodes(child)

        iter_nodes(self)

        return dirty_nodes


class Widget(AbstractNode):
    def __init__(self, *nodes):
        self.nodes = [*nodes]

    def __setattr__(self, name, value):
        if name == 'nodes':
            value = DirtyList(value)

            if hasattr(self, 'nodes'):
                old_state = super().__getattribute__('nodes')._state
                value._state = old_state
                value._check_state()

        super().__setattr__(name, value)

    # dirty ###################################################################
    @property
    def dirty(self):
        return self.nodes.dirty

    def clean(self, recursive=True):
        self.nodes.clean()

        if recursive:
            for node in self.nodes:
                if isinstance(node, AbstractNode):
                    node.clean()

    # string methods ##########################################################
    def to_string(self, node_ids=False, whitespaces=True, debug=None):
        _debug = getattr(self, 'debug', False)

        if debug is not None:
            _debug = debug

        debug = _debug

        node_string = ''

        for node in self.nodes:
            if isinstance(node, AbstractNode):
                node_string += node.to_string(
                    node_ids=node_ids,
                    whitespaces=whitespaces,
                    debug=debug,
                )

            else:
                node_string += str(node)

            if whitespaces:
                node_string += '\n'

        return node_string.strip()

    def serialize(self):
        return self.to_string(
            node_ids=True,
            whitespaces=False,
            debug=False,
        )

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    # event handling ##########################################################
    def on_click(self, input_event):
        return input_event

    def on_change(self, input_event):
        return input_event

    def on_submit(self, input_event):
        return input_event

    def on_reset(self, input_event):
        return input_event

    def handle_input_event(self, input_event):
        if input_event.name == 'click':
            return self.on_click(input_event)

        elif input_event.name == 'change':
            return self.on_change(input_event)

        elif input_event.name == 'submit':
            return self.on_submit(input_event)

        elif input_event.name == 'reset':
            return self.on_reset(input_event)

        return input_event


class Node(AbstractNode):
    INDENT_PREFIX = '  '
    TAG_NAME = 'html'
    SINGLE_TAG = False
    LONA_ATTRIBUTES = {}
    ID_LIST = []
    CLASS_LIST = []
    ATTRIBUTES = {}
    STYLE = {}

    def __init__(self, *args, **kwargs):
        # setup attributes
        self._lona_attributes = copy(self.LONA_ATTRIBUTES)
        self.id_list = copy(self.ID_LIST)
        self.class_list = copy(self.CLASS_LIST)
        self.attributes = {**copy(self.ATTRIBUTES), **kwargs}
        self.style = {}
        self.nodes = list(args)

        # remove underscores from attributes
        # this makes kwargs like '_class' possible to prevent clashes
        # with python grammar
        for key, value in self.attributes.items():
            if '_' in key:
                new_key = key.replace('_', '-')

                if new_key.startswith('-'):
                    new_key = new_key[1:]

                self.attributes[new_key] = self.attributes.pop(key)

        # unpack attributes
        if 'id' in self.attributes:
            _id = self.attributes.pop('id')

            if isinstance(_id, str):
                _id = _id.split(' ')

            self.id_list.extend(_id)

        if 'class' in self.attributes:
            _class = self.attributes.pop('class')

            if isinstance(_class, str):
                _class = _class.split(' ')

            self.class_list.extend(_class)

        if 'style' in self.attributes:
            self.style.update(self.attributes.pop('style'))

        if 'nodes' in self.attributes:
            self.nodes.extend(self.attributes.pop('nodes'))

        # lona attributes
        self._lona_attributes['id'] = \
            str(datetime.timestamp(datetime.now())).replace('.', '')

        if 'widget' not in self._lona_attributes:
            self._lona_attributes['widget'] = ''

        if 'clickable' not in self._lona_attributes:
            self._lona_attributes['clickable'] = False

        if 'changeable' not in self._lona_attributes:
            self._lona_attributes['changeable'] = False

        for name in ('id', 'widget', 'clickable', 'changeable'):
            if name in self.attributes:
                self._lona_attributes[name] = self.attributes.pop(name)

        # finish
        self.debug = False

        for attribute in [self._lona_attributes, self.id_list,
                          self.class_list, self.attributes, self.style,
                          self.nodes]:

            attribute.clean()

    # node attributes #########################################################
    def __getattribute__(self, name):
        # pass through internal attributes
        if name.startswith('_'):
            return super().__getattribute__(name)

        # node attributes
        if name in ('id', 'widget', 'clickable', 'changeable'):
            return self._lona_attributes[name]

        # pass list attributes to self.nodes
        list_attributes = (
            'append',
            'count',
            'insert',
            'reverse',
            'clear',
            'extend',
            'pop',
            'sort',
            'copy',
            'index',
            'remove',
        )

        if name in list_attributes:
            return self.nodes.__getattribute__(name)

        # node attributes
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        # node attributes
        if name == 'id':
            raise AttributeError('node id cannot be changed')

        if name in ('widget', 'clickable', 'changeable'):
            self._lona_attributes[name] = value

            return

        # dirty objects
        if name in ('_lona_attributes', 'attributes', 'style'):
            value = DirtyDict(value)

        if name in ('id_list', 'class_list', 'nodes'):
            value = DirtyList(value)

        if isinstance(value, DirtyObject) and hasattr(self, name):
            old_state = super().__getattribute__(name)._state
            value._state = old_state
            value._check_state()

        super().__setattr__(name, value)

    def __dir__(self):
        extra_names = [
            'id',
            'widget',
            'clickable',
            'changeable',
        ]

        return list(set([
            *self.nodes.__dir__(),
            *super().__dir__(),
            *extra_names,
        ]))

    # list compatibility methods ##############################################
    def __iter__(self, *args, **kwargs):
        return self.nodes.__iter__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self.nodes.__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.nodes.__setitem__(*args, **kwargs)

    # DOM helper ##############################################################
    def set_text(self, text):
        self.nodes = [text]

    def get_text(self):
        return ''.join([str(i) for i in self.nodes])

    def hide(self):
        self.style['display'] = 'none'

    def show(self):
        # FIXME: get_dirty_nodes does not recognize empty style attributes
        self.style['display'] = 'block'
