from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING
from copy import copy
import logging
import os

from lona.static_files import StyleSheet, StaticFile, Script
from lona.html.abstract_node import AbstractNode
from lona.imports import get_file

# avoid import cycles
if TYPE_CHECKING:  # pragma: no cover
    from lona.server import LonaServer

CLIENT_ROOT = os.path.join(os.path.dirname(__file__), 'client')

logger = logging.getLogger('lona.static_file_loader')


class StaticFileLoader:
    def __init__(self, server: LonaServer) -> None:
        self.server: LonaServer = server

        self.static_dirs: list[str] = [
            *self.server.settings.STATIC_DIRS,
            *self.server.settings.CORE_STATIC_DIRS,
            CLIENT_ROOT,
        ]

        # resolving potential relative paths
        for index, static_dir in enumerate(self.static_dirs):
            self.static_dirs[index] = self.server.resolve_path(static_dir)

        logger.debug('static dirs %s loaded', repr(self.static_dirs)[1:-1])

        # discover
        self.stylesheets: list[StyleSheet] = []
        self.scripts: list[Script] = []
        self.others: list[StaticFile] = []
        self.static_files: list[StaticFile] = self._discover_static_files()

        logger.debug('%d stylesheets discovered', len(self.stylesheets))
        logger.debug('%d scripts discovered', len(self.scripts))

        # render html files
        logger.debug('rendering html files')

        # stylesheets
        self.style_tags_html: str = self.server.render_template(
            self.server.settings.STATIC_FILES_STYLE_TAGS_TEMPLATE,
            {
                'stylesheets': [i for i in self.stylesheets
                                if i.enabled and i.link],
            },
        )

        # scripts
        self.script_tags_html: str = self.server.render_template(
            self.server.settings.STATIC_FILES_SCRIPT_TAGS_TEMPLATE,
            {
                'scripts': [i for i in self.scripts
                            if i.enabled and i.link],
            },
        )

    def _iter_all_declarations(self) -> Iterator[tuple[type, Iterator[StaticFile]]]:  # NOQA: LN001
        logger.debug('discover node classes')
        node_classes = AbstractNode.get_all_node_classes()
        logger.debug('%d node classes discovered', len(node_classes))

        for node_class in node_classes:
            yield node_class, iter(node_class.STATIC_FILES)

        logger.debug('discover view classes')
        view_classes = self.server._view_loader.get_all_views()
        logger.debug('%d view classes discovered', len(view_classes))

        for view_class in view_classes:
            if not hasattr(view_class, 'STATIC_FILES'):
                continue

            yield view_class, iter(view_class.STATIC_FILES)

    def _discover_static_files(self) -> list[StaticFile]:
        discovered_names: set[str] = set()
        # can't use set because StaticFileDecl is unhashable
        visited_declarations: list[StaticFile] = []

        for cls, declarations in self._iter_all_declarations():
            class_path = get_file(cls)
            class_dirname = os.path.dirname(class_path)
            context = f'{class_path}::{cls.__name__}'
            for file_declaration in declarations:
                static_file = self._process_declaration(
                    file_declaration,
                    context,
                    class_dirname,
                    visited_declarations,
                    discovered_names,
                )

                if static_file is None:
                    continue

                # sort static file into the right cache
                if isinstance(static_file, StyleSheet):
                    self.stylesheets.append(static_file)

                elif isinstance(static_file, Script):
                    self.scripts.append(static_file)

                else:
                    self.others.append(static_file)

        # sort
        self.stylesheets.sort(key=lambda x: x.sort_order.value)
        self.scripts.sort(key=lambda x: x.sort_order.value)
        self.others.sort(key=lambda x: x.sort_order.value)

        return [
            *self.stylesheets,
            *self.scripts,
            *self.others,
        ]

    def _process_declaration(
            self,
            file_declaration: StaticFile,
            context: str,
            dirname: str,
            visited: list[StaticFile],
            discovered_names: set[str],
    ) -> None | StaticFile:
        if not isinstance(file_declaration, StaticFile):
            logger.error(
                '%s: unknown type found: %r',
                context,
                file_declaration,
            )

            return None

        if file_declaration in visited:
            return None

        visited.append(file_declaration)

        if file_declaration.name in discovered_names:
            logger.error(
                "%s: static file with name '%s' already used",
                context,
                file_declaration.name,
            )

            return None

        # create a local copy
        static_file = copy(file_declaration)

        static_file.static_url_prefix = self.server.settings.STATIC_URL_PREFIX

        # patch path
        static_file_rel_path = static_file.path

        static_file_abs_path = os.path.join(dirname, static_file_rel_path)

        if not os.path.exists(static_file_abs_path):
            logger.error(
                "%s: path '%s' does not exist",
                context,
                static_file_abs_path,
            )

            return None

        static_file.path = static_file_abs_path

        # patch url
        if not static_file.url:
            url = static_file_rel_path

        else:
            url = static_file.url

        if url.startswith('/'):
            url = url[1:]

        static_file.url = url

        # disable static files that are not enabled by default and
        # are not configured to be enabled
        if (not static_file.enabled_by_default and
                (static_file.name not in
                 self.server.settings.STATIC_FILES_ENABLED)):

            static_file.enabled = False

        # disable static files that are disabled explicitly
        if static_file.name in self.server.settings.STATIC_FILES_DISABLED:
            static_file.enabled = False

        discovered_names.add(static_file.name)

        return static_file

    def resolve_path(self, path: str) -> None | str:
        logger.debug("resolving '%s'", path)

        rel_path = path

        if rel_path.startswith('/'):
            rel_path = rel_path[1:]

        # searching in static dirs
        for static_dir in self.static_dirs:
            abs_path = os.path.join(static_dir, rel_path)

            logger.debug("trying '%s'", abs_path)

            if os.path.exists(abs_path):
                if os.path.isdir(abs_path):
                    logger.debug(
                        "'%s' is directory. resolving stopped", abs_path)

                    return None

                logger.debug("returning '%s'", abs_path)

                return abs_path

        # searching in node static files
        for static_file in self.static_files:
            if not static_file.enabled:
                continue

            if static_file.url == path:
                return static_file.path

        logger.debug("'%s' was not found", path)

        return None

    def get_paths(self) -> Iterator[tuple[str, str]]:

        # copy node static files
        for static_file in self.static_files[::-1]:
            if not static_file.enabled:
                continue

            yield static_file.path, static_file.url

        # static directories
        for static_dir in self.static_dirs[::-1]:
            for name in os.listdir(static_dir):
                path = os.path.join(static_dir, name)

                yield path, name
