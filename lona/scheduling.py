from concurrent.futures import ThreadPoolExecutor, thread
import asyncio
import logging


logger = logging.getLogger('lona.scheduling.Scheduler')


DEFAULT_SCHEDULER_TASK_POOL_CONFIG = [
    ('system-high',    10),
    ('system-medium',   5),
    ('system-low',      1),

    ('service-high',   10),
    ('service-medium',  5),
    ('service-low',     1),

    ('high',           10),
    ('medium',          5),
    ('low',             1),
]

DEFAULT_SCHEDULER_THREAD_POOL_CONFIG = [
    ('system-high',    10),
    ('system-medium',   5),
    ('system-low',      1),

    ('service-high',   10),
    ('service-medium',  5),
    ('service-low',     1),

    ('high',           10),
    ('medium',          5),
    ('low',             1),
]

DEFAULT_SCHEDULER_TASK_PRIORITY = 'medium'
DEFAULT_SCHEDULER_THREAD_PRIORITY = 'medium'


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

            result = done.pop().result()

            if result == self.stopped:
                break

            coroutine, future = result

            logger.debug('%s: running %s', self.name, coroutine)

            try:
                result = await coroutine

                future.set_result(result)

            except Exception as error:
                future.set_exception(error)

        logger.debug('%s: stopped', self.name)

    def start(self):
        self.stopped = asyncio.Future()

        self.scheduler.loop.create_task(self._run())

    def stop(self):
        self.stopped.set_result(True)


class Scheduler:
    def __init__(self, loop=None,
                 task_pool_config=DEFAULT_SCHEDULER_TASK_POOL_CONFIG,
                 thread_pool_config=DEFAULT_SCHEDULER_THREAD_POOL_CONFIG,
                 default_task_priority=DEFAULT_SCHEDULER_TASK_PRIORITY,
                 default_thread_priority=DEFAULT_SCHEDULER_THREAD_PRIORITY):

        self.loop = loop or asyncio.get_event_loop()
        self.task_pool_config = task_pool_config
        self.thread_pool_config = thread_pool_config
        self.default_task_priority = default_task_priority
        self.default_thread_priority = default_thread_priority

        # setup task pools
        self.task_priority_map = {}
        self.task_queues = {}
        self.task_workers = {}

        for priority_name, max_workers in self.task_pool_config:
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

        for priority_name, max_workers in self.thread_pool_config:
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

        priority = priority or self.default_task_priority

        if asyncio.iscoroutinefunction(coroutine):
            coroutine = coroutine(*args, **kwargs)

        future = asyncio.Future()
        self.task_queues[priority].put_nowait((coroutine, future,))

        if not sync:
            return future

        concurrent_future = asyncio.wrap_future(future)

        if wait:
            return future.result()

        return concurrent_future

    def schedule_function(self, function, *args, priority=None, sync=False,
                          wait=True, **kwargs):

        def run_function():
            logger.debug('running %s', function)

            function(*args, **kwargs)

        priority = priority or self.default_thread_priority
        executor = self.thread_pools[priority]
        future = self.loop.run_in_executor(executor, run_function)

        if not sync:
            return future

        concurrent_future = asyncio.wrap_future(future)

        if wait:
            return future.result()

        return concurrent_future

    def schedule(self, function_or_coroutine, *args, priority=None, sync=False,
                 wait=True, **kwargs):

        # TODO: implement

        raise NotImplementedError
