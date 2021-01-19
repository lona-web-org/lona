import logging

logger = logging.getLogger('test_project')


def server_start(server):
    logger.debug('%s running hooks.server_start', repr(server))


def server_stop(server):
    logger.debug('%s running hooks.server_stop', repr(server))
