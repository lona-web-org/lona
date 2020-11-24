import logging

from lona.utils import acquire

logger = logging.getLogger('lona.hooks')


class HookManager:
    # TODO: custom priorities

    def __init__(self, server):
        self.server = server

        self._discover_hooks()

    def _discover_hooks(self):
        logger.debug('discovering hooks')

        self._hooks = {}

        def _add_hook(hook_name, hook):
            logger.debug('%s: %s discovered', hook_name, hook)

            self._hooks[hook_name].append(hook)

        for hook_name, hooks in self.server.settings.HOOKS.items():
            if not isinstance(hooks, list):
                hooks = [hooks]

            self._hooks[hook_name] = []

            for hook in hooks:
                if callable(hook):
                    _add_hook(hook_name, hook)

                elif isinstance(hook, str):
                    try:
                        path, attribute = acquire(hook)

                    except Exception:
                        logger.error(
                            "Exception raise while importing '%s'",
                            hook,
                            exc_info=True,
                        )

                        continue

                    if not callable(attribute):
                        logger.error("hook '%s' is not callable", hook)

                        continue

                    _add_hook(hook_name, hook)

                else:
                    logger.error('hooks have to be either a callable or an import string')  # NOQA

    def run(self, name, *args, **kwargs):
        logger.debug('running hook %s', name)

        if name not in self._hooks:
            return

        for hook in self._hooks[name]:
            logger.debug('running hook %s: %s scheduled', name, hook)

            try:
                self.server.scheduler.schedule(
                    hook,
                    *args,
                    **kwargs,
                    priority=self.server.settings.DEFAULT_HOOK_PRIORITY,
                    sync=True,
                    wait=True,
                )

            except Exception:
                logger.error(
                    'hook %s: %s raised an exception',
                    name,
                    hook,
                    exc_info=True,
                )
