import inspect
import logging
import os

from lona.utils import acquire

logger = logging.getLogger('lona.view_loader')


class ViewSpec:
    # TODO: add support for async views
    # TODO: find view priority

    def __init__(self, view):
        self.view = view

        self.multi_user = getattr(self.view, 'multi_user', False)
        self.is_class_based = False
        self.has_input_event_handler = False
        self.has_root_input_event_handler = False

        if inspect.isclass(self.view):
            self.is_class_based = True

            self.has_input_event_handler = hasattr(
                self.view, 'handle_input_event')

            self.has_root_input_event_handler = hasattr(
                self.view, 'handle_root_input_event')


class ViewLoader:
    # TODO: add api to load 404 and 500 handler

    def __init__(self, server):
        self.server = server

        self._view_cache = {
            # contains: {
            #     import_string: {
            #         'path': path,
            #         'view': view,
            #         'modified': modified,  # return value of os.path.getmtime
            #     }
            # }
        }

        self._view_spec_cache = {
            # contains {
            #     import_string: view_spec,
            # }
        }

    def _load_into_cache(self, import_string, ignore_import_cache):
        logger.debug("importing '%s' ignore_import_cache=%s",
                     import_string, repr(ignore_import_cache))

        path, view = acquire(
            import_string, ignore_import_cache=ignore_import_cache)

        logger.debug("'%s' imported from '%s'", import_string, path)

        self._view_cache[import_string] = {
            'path': path,
            'view': view,
            'modified': os.path.getmtime(path),
        }

        self._view_spec_cache[view] = ViewSpec(view)

    def load(self, import_string):
        logger.debug("loading '%s'", import_string)

        if isinstance(import_string, str):
            caching_enabled = self.server.settings.VIEW_CACHING
            ignore_import_cache = not caching_enabled

            if import_string not in self._view_cache:
                logger.debug("'%s' is not cached yet", import_string)

                self._load_into_cache(import_string, ignore_import_cache)

            elif not caching_enabled:
                path = self._view_cache[import_string]['path']
                modified = self._view_cache[import_string]['modified']

                if os.path.getmtime(path) > modified:
                    logger.debug("'%s' is modified in file system",
                                 import_string)

                    self._load_into_cache(import_string, ignore_import_cache)

            else:
                logger.debug("loading '%s' from cache", import_string)

        else:
            if import_string not in self._view_spec_cache:
                self._view_spec_cache[import_string] = ViewSpec(import_string)

            return import_string

        return self._view_cache[import_string]['view']

    def get_view_spec(self, view):
        return self._view_spec_cache[view]
