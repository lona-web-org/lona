import logging
import os

logger = logging.getLogger('lona')

CLIENT_VERSION_ENV_VAR_NAME = 'LONA_CLIENT_VERSION'
CLIENT_VERSION_ENV_VAR_VALUES = (1, 2)

USE_FUTURE_NODE_CLASSES_ENV_VAR_NAME = 'LONA_USE_FUTURE_NODE_CLASSES'
USE_FUTURE_NODE_CLASSES_ENV_VAR_VALUES = (True, False)


# client version ##############################################################
def get_client_version():
    # TODO: remove in 2.0

    client_version = int(os.environ.get(CLIENT_VERSION_ENV_VAR_NAME, '1'))

    if client_version not in CLIENT_VERSION_ENV_VAR_VALUES:
        logger.error(
            'invalid env variable: %s=%s',
            CLIENT_VERSION_ENV_VAR_NAME,
            client_version,
        )

        return 1

    return client_version


def set_client_version(version):
    # TODO: remove in 2.0

    if version not in CLIENT_VERSION_ENV_VAR_VALUES:
        raise RuntimeError(f'invalid client version number: {version}')

    version = str(version)

    os.environ[CLIENT_VERSION_ENV_VAR_NAME] = version

    logger.debug('client version is set to %s', version)


# future node classes #########################################################
def get_use_future_node_classes():
    # TODO: remove in 2.0

    raw_use_future_node_classes = os.environ.get(
        USE_FUTURE_NODE_CLASSES_ENV_VAR_NAME,
        'false',
    )

    use_future_node_classes = {
        'true': True,
        'false': False,
        '1': True,
        '0': False,
    }[raw_use_future_node_classes.strip().lower()]

    if use_future_node_classes not in USE_FUTURE_NODE_CLASSES_ENV_VAR_VALUES:
        logger.error(
            'invalid env variable: %s=%s',
            USE_FUTURE_NODE_CLASSES_ENV_VAR_NAME,
            raw_use_future_node_classes,
        )

        return False

    return use_future_node_classes


def set_use_future_node_classes(enabled):
    # TODO: remove in 2.0

    if enabled not in USE_FUTURE_NODE_CLASSES_ENV_VAR_VALUES:
        raise RuntimeError(f'invalid value for {USE_FUTURE_NODE_CLASSES_ENV_VAR_NAME}: {enabled}')

    enabled = str(enabled)

    os.environ[USE_FUTURE_NODE_CLASSES_ENV_VAR_NAME] = enabled

    logger.debug('%s set to %s', USE_FUTURE_NODE_CLASSES_ENV_VAR_NAME, enabled)
