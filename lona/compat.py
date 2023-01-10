import logging
import os

logger = logging.getLogger('lona')

CLIENT_VERSION_ENV_VAR_NAME = 'LONA_CLIENT_VERSION'
CLIENT_VERSION_ENV_VAR_VALUES = (1, 2)


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
