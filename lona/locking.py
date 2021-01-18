import asyncio

from lona.context import get_current_context_name


class LockContextManager:
    def __init__(self, lock_manager, context_name):
        self.lock_manager = lock_manager
        self.context_name = context_name

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.lock_manager._release(self.context_name)


class LockManager:
    def __init__(self, loop=None, pass_through_mode=False):
        self.pass_through_mode = pass_through_mode
        self.loop = loop

        self._locks = [
            # [context_name, started, lock_context_counter],
        ]

    async def _await(self, future):
        return await future

    def _release(self, context_name):
        if self.pass_through_mode or not self.loop:
            return

        for lock in self._locks:
            if lock[0] != context_name:
                continue

            lock[2] -= 1

            if lock[2] == 0:
                self._locks.remove(lock)

            if(self._locks and
               not self._locks[0][1].done() and
               not self._locks[0][1].cancelled()):

                self._locks[0][1].set_result(True)

    def lock(self):
        if self.pass_through_mode or not self.loop:
            return LockContextManager(self, '')

        context_name = get_current_context_name()
        context_manager = LockContextManager(self, context_name)
        lock = []

        for _lock in self._locks:
            if _lock[0] == context_name:
                lock = _lock

                break

        if not lock:
            lock = [context_name, asyncio.Future(loop=self.loop), 0]
            self._locks.append(lock)

        started = lock[1]

        if(self._locks.index(lock) == 0 and
           not started.done() and
           not started.cancelled()):

            started.set_result(True)

        lock[2] += 1

        if not started.done() and not started.cancelled():
            asyncio.run_coroutine_threadsafe(
                self._await(started),
                loop=self.loop,
            ).result()

        return context_manager
