import logging
import os

from lona.utils import acquire

logger = logging.getLogger('lona.view_loader')


class ViewLoader:
    # TODO: add cache pre loading (necessary for static file discovery)
    # TODO: add api to load 404 and 500 handler
    # TODO: add view inspection

    def __init__(self, server):
        self.server = server

        self.cache = {
            # import_string: {
            #     'path': path,
            #     'view': view,
            #     'modified': modified,  # return value of os.path.getmtime
            # }
        }

    def _load_into_cache(self, import_string, ignore_import_cache):
        logger.debug("importing '%s' ignore_import_cache=%s",
                     import_string, repr(ignore_import_cache))

        path, view = acquire(
            import_string, ignore_import_cache=ignore_import_cache)

        logger.debug("'%s' imported from '%s'", import_string, path)

        self.cache[import_string] = {
            'path': path,
            'view': view,
            'modified': os.path.getmtime(path),
        }

    def load(self, import_string):
        logger.debug("loading '%s'", import_string)

        caching_enabled = self.server.settings.VIEW_CACHING
        ignore_import_cache = not caching_enabled

        if import_string not in self.cache:
            logger.debug("'%s' is not cached yet", import_string)

            self._load_into_cache(import_string, ignore_import_cache)

        elif not caching_enabled:
            path = self.cache[import_string]['path']
            modified = self.cache[import_string]['modified']

            if os.path.getmtime(path) > modified:
                logger.debug("'%s' is modified in file system", import_string)

                self._load_into_cache(import_string, ignore_import_cache)

        else:
            logger.debug("loading '%s' from cache", import_string)

        return self.cache[import_string]['view']
