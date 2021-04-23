import re

SELECTOR_RE = re.compile(r'([#.])?(([^#.\[\]]+)|(\[([^=\[\]]+)=([^=\[\]]+)\]))')  # NOQA
UNSUPPORTED_CHARACTERS = re.compile(r'([ $|!~>+])')


class Selector:
    def __init__(self, raw_selector_string):
        self.raw_selector_string = raw_selector_string

        self.check_raw_selector_string()
        self.parse_selector()

    def __repr__(self):
        return '<{}({})>'.format(
            self.__class__.__name__,
            repr(self.selectors),
        )

    def check_raw_selector_string(self):
        match = UNSUPPORTED_CHARACTERS.search(self.raw_selector_string)

        if match:
            raise ValueError(
                'unsupported selector feature: {}'.format(repr(match.group())),
            )

    def parse_selector(self):
        self.selectors = []

        selector_strings = self.raw_selector_string.split(',')

        for selector_string in selector_strings:
            selector = {
                'tag_name': '',
                'ids': [],
                'classes': [],
                'attributes': {},
            }

            for match in SELECTOR_RE.findall(selector_string):
                prefix, name, _, _, attribute_name, attribute_value = match

                if prefix == '#':
                    selector['ids'].append(name)

                elif prefix == '.':
                    selector['classes'].append(name)

                elif not prefix and not attribute_name:
                    selector['tag_name'] = name

                elif attribute_name and attribute_value:
                    attribute_value = attribute_value.replace('"', '')
                    attribute_value = attribute_value.replace("'", '')

                    selector['attributes'][attribute_name] = attribute_value

            self.selectors.append(selector)

    def _match_selector(self, node, selector):
        # tag name
        if selector['tag_name']:
            if not hasattr(node, 'tag_name'):
                return False

            if node.tag_name != selector['tag_name']:
                return False

        # ids
        if selector['ids']:
            if not hasattr(node, 'id_list'):
                return False

            for id_name in selector['ids']:
                if id_name not in node.id_list:
                    return False

        # classes
        if selector['classes']:
            if not hasattr(node, 'class_list'):
                return False

            for class_name in selector['classes']:
                if class_name not in node.class_list:
                    return False

        # attributes
        if selector['attributes']:
            if not hasattr(node, 'attributes'):
                return False

            for name, value in selector['attributes'].items():
                if name not in node.attributes:
                    return False

                if node.attributes[name] != value:
                    return False

        return True

    def match(self, node):
        for selector in self.selectors:
            if self._match_selector(node, selector):
                return True

        return False
