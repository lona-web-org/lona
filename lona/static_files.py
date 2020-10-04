import logging
import os

logger = logging.getLogger('lona.static_files')


class StaticFileLoader:
    def __init__(self, server):
        self.server = server

        self.static_dirs = (self.server.settings.STATIC_DIRS +
                            self.server.settings.CORE_STATIC_DIRS)

        logger.debug('static dirs %s loaded', repr(self.static_dirs)[1:-1])

    def resolve_path(self, path):
        logger.debug("resolving '%s'", path)

        if path.startswith('/'):
            path = path[1:]

        for static_dir in self.static_dirs[::-1]:
            abs_path = os.path.join(static_dir, path)

            logger.debug("trying '%s'", abs_path)

            if os.path.exists(abs_path):
                if os.path.isdir(abs_path):
                    logger.debug(
                        "'%s' is directory. resolving stopped", abs_path)

                    return

                logger.debug("returning '%s'", abs_path)

                return abs_path

        logger.debug("'%s' was not found", path)
