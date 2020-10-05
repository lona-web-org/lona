from copy import copy
import logging
import inspect
import os

from lona.html.base import AbstractNode

logger = logging.getLogger('lona.static_files')


class SortOrder:
    FRAMEWORK = 100
    LIBRARY = 200
    APPLICATION = 300


class StaticFile:
    def __init__(self, name, path, url=None, sort_order=None, link=True):
        self.name = name
        self.path = path
        self.url = url
        self.sort_order = sort_order or SortOrder.APPLICATION
        self.link = link

        # this value is only for the object representation
        # and is meant for debugging
        self.static_url_prefix = ''

    def __repr__(self):
        return '<{}({}, {}{} -> {})>'.format(
            self.__class__.__name__,
            self.name,
            self.static_url_prefix,
            self.url,
            self.path,
        )


class StyleSheet(StaticFile):
    pass


class Script(StaticFile):
    pass


class StaticFileLoader:
    def __init__(self, server):
        self.server = server

        self.static_dirs = (self.server.settings.STATIC_DIRS +
                            self.server.settings.CORE_STATIC_DIRS)

        logger.debug('static dirs %s loaded', repr(self.static_dirs)[1:-1])

        self.discover()

    def discover_node_classes(self):
        # TODO: implement whitelisting and blacklisting

        node_classes = [AbstractNode]

        while True:
            count = len(node_classes)

            for node_class in list(node_classes):
                for sub_class in node_class.__subclasses__():
                    if sub_class not in node_classes:
                        node_classes.append(sub_class)

            if len(node_classes) == count:
                return node_classes

    def discover_node_static_files(self):
        # TODO: implement whitelisting and blacklisting

        node_stylesheets = []
        node_scripts = []

        # discover
        discovered_names = []

        for node_class in self.node_classes:
            if not hasattr(node_class, 'STATIC_FILES'):
                continue

            for static_file in node_class.STATIC_FILES:
                if static_file.name not in discovered_names:
                    # create a local copy
                    static_file = copy(static_file)

                    static_file.static_url_prefix = \
                        self.server.settings.STATIC_URL_PREFIX

                    # patch path
                    static_file_rel_path = static_file.path
                    node_class_path = inspect.getfile(node_class)
                    node_class_dirname = os.path.dirname(node_class_path)

                    static_file_abs_path = os.path.join(
                        node_class_dirname, static_file_rel_path)

                    if not os.path.exists(static_file_abs_path):
                        # TODO: error message

                        continue

                    static_file.path = static_file_abs_path

                    # patch url
                    if not static_file.url:
                        url = static_file_rel_path

                    else:
                        url = static_file.url

                    if url.startswith('/'):
                        url = url[1:]

                    static_file.url = url

                    # sort static file into the right cache
                    if isinstance(static_file, StyleSheet):
                        node_stylesheets.append(static_file)

                    elif isinstance(static_file, Script):
                        node_scripts.append(static_file)

                    else:
                        # TODO: error message

                        continue

                    discovered_names.append(static_file.name)

        # sort
        node_stylesheets = sorted(node_stylesheets, key=lambda x: x.sort_order)
        node_scripts = sorted(node_scripts, key=lambda x: x.sort_order)

        return node_stylesheets, node_scripts

    def discover(self):
        logger.debug('discover node classes')

        self.node_classes = self.discover_node_classes()

        self.node_stylesheets, self.node_scripts = \
            self.discover_node_static_files()

        logger.debug('%s node classes discovered', len(self.node_classes))

        logger.debug('%s node stylesheets discovered',
                     len(self.node_stylesheets))

        logger.debug('%s node scripts discovered', len(self.node_scripts))

        # render html files
        logger.debug('rendering html files')

        # TODO: make templates configurable
        # stylesheets
        self.style_tags_html = self.server.templating_engine.render_template(
            'lona/style_tags.html',
            {
                'stylesheets': self.node_stylesheets,
            }
        )

        # scripts
        self.script_tags_html = self.server.templating_engine.render_template(
            'lona/script_tags.html',
            {
                'scripts': self.node_scripts,
            }
        )

    def resolve_path(self, path):
        logger.debug("resolving '%s'", path)

        rel_path = path

        # searching in static dirs
        if rel_path.startswith('/'):
            rel_path = rel_path[1:]

        for static_dir in self.static_dirs[::-1]:
            abs_path = os.path.join(static_dir, rel_path)

            logger.debug("trying '%s'", abs_path)

            if os.path.exists(abs_path):
                if os.path.isdir(abs_path):
                    logger.debug(
                        "'%s' is directory. resolving stopped", abs_path)

                    return

                logger.debug("returning '%s'", abs_path)

                return abs_path

        # searching in node static files
        for static_file in self.node_stylesheets + self.node_scripts:
            if static_file.url == path:
                return static_file.path

        logger.debug("'%s' was not found", path)
