from copy import copy
import logging
import os

from lona.static_files import StaticFile, StyleSheet, Script
from lona.html.abstract_node import AbstractNode
from lona.imports import get_file

logger = logging.getLogger('lona.static_file_loader')


class StaticFileLoader:
    def __init__(self, server):
        self.server = server

        self.static_dirs = self.server.settings.STATIC_DIRS.copy()

        # resolving potential relative paths
        for index, static_dir in enumerate(self.static_dirs):
            self.static_dirs[index] = self.server.resolve_path(static_dir)

        logger.debug('static dirs %s loaded', repr(self.static_dirs)[1:-1])

        self.discover()

    def discover_node_classes(self):
        self.node_classes = [AbstractNode]

        while True:
            count = len(self.node_classes)

            for node_class in list(self.node_classes):
                for sub_class in node_class.__subclasses__():
                    if sub_class not in self.node_classes:
                        self.node_classes.append(sub_class)

            if len(self.node_classes) == count:
                return self.node_classes

    def discover_node_static_files(self):
        self.node_stylesheets = []
        self.node_scripts = []
        self.node_static_files = []
        self.static_files = []

        # discover
        discovered_names = []

        for node_class in self.node_classes:
            if not hasattr(node_class, 'STATIC_FILES'):
                continue

            for static_file in node_class.STATIC_FILES:
                if static_file.name in discovered_names:
                    continue

                node_class_path = get_file(node_class)
                node_class_dirname = os.path.dirname(node_class_path)

                # check static file
                if not isinstance(static_file, StaticFile):
                    logger.error(
                        '%s::%s: unknown type found: %s',
                        node_class_path,
                        node_class.__name__,
                        repr(static_file),
                    )

                    continue

                # create a local copy
                static_file = copy(static_file)

                static_file.static_url_prefix = \
                    self.server.settings.STATIC_URL_PREFIX

                # patch path
                static_file_rel_path = static_file.path

                static_file_abs_path = os.path.join(
                    node_class_dirname, static_file_rel_path)

                if not os.path.exists(static_file_abs_path):
                    logger.error(
                        "%s::%s: path '%s' does not exist",
                        node_class_path,
                        node_class.__name__,
                        static_file_abs_path,
                    )

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
                    self.node_stylesheets.append(static_file)

                elif isinstance(static_file, Script):
                    self.node_scripts.append(static_file)

                else:
                    self.node_static_files.append(static_file)

                discovered_names.append(static_file.name)

        # sort
        self.node_stylesheets = sorted(
            self.node_stylesheets, key=lambda x: x.sort_order)

        self.node_scripts = sorted(
            self.node_scripts, key=lambda x: x.sort_order)

        # enable or disable static files
        self.static_files = [
            *self.node_stylesheets,
            *self.node_scripts,
            *self.node_static_files,
        ]

        for static_file in self.static_files:
            # disable static files that are not enabled by default and
            # are not configured to be enabled
            if(not static_file.enabled_by_default and
               static_file.name not in
               self.server.settings.STATIC_FILES_ENABLED):

                static_file.enabled = False

            # disable static files that are disabled explicitly
            if static_file.name in self.server.settings.STATIC_FILES_DISABLED:
                static_file.enabled = False

    def discover(self):
        logger.debug('discover node classes')

        self.discover_node_classes()
        self.discover_node_static_files()

        logger.debug('%s node classes discovered', len(self.node_classes))

        logger.debug('%s node stylesheets discovered',
                     len(self.node_stylesheets))

        logger.debug('%s node scripts discovered', len(self.node_scripts))

        # render html files
        logger.debug('rendering html files')

        # stylesheets
        self.style_tags_html = self.server.templating_engine.render_template(
            self.server.settings.STATIC_FILES_STYLE_TAGS_TEMPLATE,
            {
                'stylesheets': [i for i in self.node_stylesheets if i.enabled],
            }
        )

        # scripts
        self.script_tags_html = self.server.templating_engine.render_template(
            self.server.settings.STATIC_FILES_SCRIPT_TAGS_TEMPLATE,
            {
                'scripts': [i for i in self.node_scripts if i.enabled],
            }
        )

    def resolve_path(self, path):
        logger.debug("resolving '%s'", path)

        rel_path = path

        if rel_path.startswith('/'):
            rel_path = rel_path[1:]

        # javascript client
        client_url = self.server.settings.STATIC_FILES_CLIENT_URL

        if client_url.startswith('/'):
            client_url = client_url[1:]

        if rel_path == client_url:
            logger.debug('returning javascript client')

            return self.server.client_pre_compiler.resolve()

        # searching in static dirs
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
        for static_file in self.static_files:
            if not static_file.enabled:
                continue

            if static_file.url == path:
                return static_file.path

        logger.debug("'%s' was not found", path)
