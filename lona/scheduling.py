from concurrent.futures import ThreadPoolExecutor, thread
import threading
import traceback
import asyncio
import logging

logger = logging.getLogger('lona.scheduling.Scheduler')


def get_current_thread_name():
    thread_name = threading.currentThread().getName()

    if thread_name == 'MainThread':
        for frame in traceback.extract_stack()[::-1]:
            if frame.filename.startswith('<lona-zone'):
                thread_name = frame.filename.split('"')[1]

                break

    return thread_name


class TaskWorker:
    def __init__(self, scheduler, name, priority, queue):
        self.scheduler = scheduler
        self.name = name
        self.priority = priority
        self.queue = queue

    async def _run(self):
        logger.debug('%s: started', self.name)

        while True:
            logger.debug('%s: waiting', self.name)

            done, pending = await asyncio.wait(
                [
                    self.stopped,
                    self.queue.get(),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            done = done.pop()

            if done == self.stopped:
                for future in pending:
                    future.cancel()

                break

            coroutine, future = done.result()

            logger.debug('%s: running %s', self.name, coroutine)

            try:
                result = await coroutine

                if not future.done() and not future.cancelled():
                    future.set_result(result)

            except Exception as error:
                if not future.done() and not future.cancelled():
                    future.set_exception(error)

            finally:
                self.queue.task_done()

        logger.debug('%s: stopped', self.name)

    def start(self):
        self.stopped = asyncio.Future()

        task = self._run()

        # mark the currently running zone
        file_name = '<lona-zone-"{}">'.format(self.name)

        code_text = """
            async def run(coroutine):
                return await coroutine
        """.strip()

        code = compile(code_text, file_name, 'exec')
        exec(code)
        coroutine = locals()['run']

        task = coroutine(task)

        # create task
        self.scheduler.loop.create_task(task)

    def stop(self):
        self.stopped.set_result(True)


class Scheduler:
    def __init__(self, loop=None, task_zones=[], thread_zones=[]):
        self.loop = loop or asyncio.get_event_loop()
        self.task_zones = task_zones
        self.thread_zones = thread_zones

        # setup task pools
        self.task_priority_map = {}
        self.task_queues = {}
        self.task_workers = {}

        for priority_name, max_workers in self.task_zones:
            queue = asyncio.Queue()

            self.task_priority_map[priority_name] = max_workers
            self.task_queues[priority_name] = queue
            self.task_workers[priority_name] = []

            # setup worker
            for i in range(max_workers):
                worker_name = '{} PriorityTask_{}'.format(priority_name, i)

                worker = TaskWorker(
                    name=worker_name,
                    scheduler=self,
                    priority=priority_name,
                    queue=queue,
                )

                self.task_workers[priority_name].append(worker)

        # setup thread pools
        self.thread_priority_map = {}
        self.thread_pools = {}

        for priority_name, max_workers in self.thread_zones:
            executor = ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix='{} PriorityThread'.format(priority_name),
            )

            self.thread_priority_map[priority_name] = max_workers
            self.thread_pools[priority_name] = executor

    def start(self):
        # tasks
        for priority_name, task_workers in self.task_workers.items():
            for task in task_workers:
                task.start()

    def stop(self, graceful=True):
        # tasks
        for priority_name, task_workers in self.task_workers.items():
            for task in task_workers:
                task.stop()

        # threads
        for priority_name, executor in self.thread_pools.items():
            if graceful:
                executor.shutdown()

            else:
                executor._threads.clear()

        if not graceful:
            thread._threads_queues.clear()

    # public api ##############################################################
    def schedule_coroutine(self, coroutine, *args, priority=None, sync=False,
                           wait=True, **kwargs):

        async def await_future(future):
            return await future

        if not priority:
            raise ValueError('no priority set')

        if asyncio.iscoroutinefunction(coroutine):
            coroutine = coroutine(*args, **kwargs)

        future = asyncio.Future(loop=self.loop)
        self.task_queues[priority].put_nowait((coroutine, future,))

        if not sync:
            return future

        concurrent_future = asyncio.run_coroutine_threadsafe(
            await_future(future),
            loop=self.loop,
        )

        if not wait:
            return concurrent_future

        return concurrent_future.result()

    def schedule_function(self, function, *args, priority=None, sync=False,
                          wait=True, **kwargs):

        def run_function():
            logger.debug('running %s', function)

            return function(*args, **kwargs)

        async def await_future(future):
            return await future

        if not priority:
            raise ValueError('no priority set')

        executor = self.thread_pools[priority]
        future = self.loop.run_in_executor(executor, run_function)

        if not sync:
            return future

        concurrent_future = asyncio.run_coroutine_threadsafe(
            await_future(future),
            loop=self.loop,
        )

        if not wait:
            return concurrent_future

        return concurrent_future.result()

    def schedule(self, function_or_coroutine, *args, priority=None, sync=False,
                 wait=True, **kwargs):

        if(asyncio.iscoroutine(function_or_coroutine) or
           asyncio.iscoroutinefunction(function_or_coroutine)):

            return self.schedule_coroutine(
                function_or_coroutine,
                *args,
                priority=priority,
                sync=sync,
                **kwargs,
            )

        else:
            return self.schedule_function(
                function_or_coroutine,
                *args,
                priority=priority,
                sync=sync,
                **kwargs,
            )
