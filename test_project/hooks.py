import logging

logger = logging.getLogger('test_project')


async def server_startup(app):
    logger.debug('%s running hooks.server_startup', repr(app['lona_server']))


async def server_shutdown(app):
    logger.debug('%s running hooks.server_shutdown', repr(app['lona_server']))
