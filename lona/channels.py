from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Dict
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta, datetime
from queue import Queue, Empty
from logging import getLogger
from fnmatch import fnmatch
from threading import Lock
from copy import copy

logger = getLogger('lona.channels')

if TYPE_CHECKING:  # pragma: no cover
    from lona.server import Server


def clear_queue(queue: Queue) -> None:
    while not queue.empty():
        try:
            queue.get(block=False)

        except Empty:  # pragma: no cover
            continue

        queue.task_done()


def match(topic_a: str, topic_b: str) -> bool:
    if topic_a == topic_b:
        return True

    if fnmatch(topic_a, topic_b):
        return True

    if fnmatch(topic_b, topic_a):
        return True

    return False


class Message:
    def __init__(
            self,
            topic: str,
            data: dict,
            expiry: datetime | None = None,
            local: bool = False,
            droppable: bool = False,
    ):

        self.topic: str = topic
        self.data: dict = copy(data)
        self.expiry: datetime | None = expiry
        self.local: bool = local
        self.droppable: bool = droppable

        self._original_message: Message | None = None
        self._is_dropped: bool = False

    def __repr__(self):
        return f'<Message(topic={self.topic!r}, data={self.data!r})>'

    def copy(self) -> Message:
        message: Message = Message(
            topic=self.topic,
            data=self.data,
            expiry=self.expiry,
            local=self.local,
            droppable=self.droppable,
        )

        message._original_message = self._original_message or self

        return message

    def is_expired(self) -> bool:
        if not self.expiry:
            return False

        return self.expiry <= datetime.now()

    def is_dropped(self) -> bool:
        if self._original_message:
            return self._original_message._is_dropped

        return self._is_dropped

    def drop_if_possible(self, worker_is_running: bool) -> bool:
        drop: bool = False
        drop_message: str = ''

        # original message was dropped
        if self._original_message and self._original_message._is_dropped:
            drop = True
            drop_message = ' is dropped'

        # message was dropped
        elif self._is_dropped:
            drop = True
            drop_message = ' is dropped'

        # message is expired
        elif self.is_expired():
            drop = True
            drop_message = ' is expired'

        # drop on shutdown
        if not worker_is_running and self.droppable:
            drop = True
            drop_message = ' is expired to shutdown worker'

        # drop message
        if drop:
            logger.debug('%s %s', self, drop_message)

            if self._original_message:
                self._original_message._is_dropped = True

            else:
                self._is_dropped = True

        return drop


class Task:
    def __init__(self, channel: Channel, message: Message):
        self.channel: Channel = channel
        self.message: Message = message


class Channel:
    _channels: Dict[str, List[Channel]] = {}
    _messages: Queue[Message] = Queue()
    _tasks: Queue[Task] = Queue()
    _lock: Lock = Lock()

    def __init__(self, topic: str, handler: Callable | None = None):
        self._topic: str = topic
        self._handler: Callable | None = None

        if handler:
            self.subscribe(handler=handler)

    def __repr__(self):
        return f'<Channel(topic={self.topic!r}), handler={self.handler!r}>'

    # class API
    @classmethod
    def _clear_state(cls):
        logger.debug('clearing state')

        while cls._channels:
            topic = list(cls._channels.keys())[0]

            for channel in cls._channels[topic].copy():
                channel.unsubscribe()

        clear_queue(cls._messages)
        clear_queue(cls._tasks)

        logger.debug('state cleared')

    @classmethod
    def get_channels(cls, topic: str) -> List[Channel]:
        topics = list(cls._channels.keys())
        channels = []

        for _topic in topics:
            if not match(_topic, topic):
                continue

            channels.extend(cls._channels.get(_topic, []))

        return channels

    # object API
    @property
    def topic(self) -> str:
        return self._topic

    @property
    def handler(self) -> Callable | None:
        return self._handler

    def subscribe(self, handler: Callable) -> None:
        if self._handler:
            raise RuntimeError('channel is already subscribed')

        self._handler = handler

        logger.debug('subscribing to %s', self)

        with self._lock:
            if self.topic not in self._channels:
                self._channels[self.topic] = []

            self._channels[self.topic].append(self)

        Channel('lona.channels.subscribe').send(
            message_data={'topic': self.topic},
            local=True,
        )

    def unsubscribe(self) -> None:
        if self._handler is None:  # pragma: no cover
            return

        logger.debug('unsubscribing from %s', self)

        self._handler = None

        with self._lock:
            self._channels[self.topic].remove(self)

            if not self._channels[self.topic]:
                self._channels.pop(self.topic)

        Channel('lona.channels.unsubscribe').send(
            message_data={'topic': self.topic},
            local=True,
        )

    def send(
            self,
            message_data: dict | None = None,
            expiry: datetime | timedelta | None = None,
            local: bool = False,
            droppable: bool = False,
    ) -> Message:

        """
        Send a message to all channels subscribed to a matching topic.

        :message_data:  Optional user-defined message payload. When given a
                        dict it gets shallow copied using `copy.copy` to ensure
                        message integrity between multiple scopes.

        :expiry:        When set to a datetime- or timedelta object, the
                        message gets dropped if it expires before being
                        handled.

        :local:         Tells the broker if a message should be handled process
                        local or not. Has no effect when using the
                        default broker.

        :droppable:     Tells the broker and the task worker if a message may
                        be dropped for faster shutdown.
        """

        if isinstance(expiry, timedelta):
            expiry = datetime.now() + expiry

        message = Message(
            topic=self.topic,
            data=message_data or {},
            expiry=expiry,
            local=local,
            droppable=droppable,
        )

        self._messages.put_nowait(message)

        return message


class Worker:
    def __init__(
            self,
            server: 'Server',
            executor: ThreadPoolExecutor,
            timeout: float,
    ):

        self.server: 'Server' = server
        self.executor: ThreadPoolExecutor = executor

        # runtime state
        self.running: bool = True
        self.timeout: float = timeout
        self.block: bool = True

        # start thread
        self.executor.submit(self._run)

    def shutdown(self):
        self.running = False
        self.block = False
        self.timeout = 0

    def get_message(self) -> Message:
        message: Message = Channel._messages.get(
            block=self.block,
            timeout=self.timeout,
        )

        dropped: bool = message.drop_if_possible(
            worker_is_running=self.running,
        )

        if dropped:
            raise Empty

        return message

    def get_task(self) -> Task:
        task: Task = Channel._tasks.get(
            block=self.block,
            timeout=self.timeout,
        )

        dropped: bool = task.message.drop_if_possible(
            worker_is_running=self.running,
        )

        if dropped:
            raise Empty

        return task

    def schedule_task(self, channel: Channel, message: Message) -> None:
        Channel._tasks.put(
            Task(
                channel=channel,
                message=message.copy(),
            ),
        )

    def _run(self) -> None:
        while True:
            try:
                self.run()

            except (TimeoutError, Empty) as exception:
                if not self.running and isinstance(exception, Empty):
                    break

    def run(self) -> None:  # pragma: no cover
        raise NotImplementedError()


class MessageBroker(Worker):
    # derived from lona.channels.Worker

    def run(self):

        # get message from global message queue
        # this queue gets filled by lona.Channel.send()
        message = self.get_message()

        # get all channels that are subscribed to message.topic
        channels = Channel.get_channels(topic=message.topic)

        # schedule a task for each channel
        for channel in channels:
            self.schedule_task(
                channel=channel,
                message=message,
            )

        logger.debug(
            '%s tasks scheduled for %s',
            len(channels),
            message,
        )


class TaskWorker(Worker):
    # derived from lona.channels.Worker

    def run(self):

        # get task from global task queue
        # this queue gets filled by lona.Worker.schedule_task()
        task = self.get_task()

        logger.debug(
            'running %s with message %s',
            task.channel.handler,
            task.message,
        )

        # run handler
        handler = task.channel.handler

        try:
            if not handler:  # pragma: no cover
                logger.debug('channel unsubscribed while running its handler')

                return

            handler(task.message)

        except Exception:
            logger.exception(
                'exception was raised while running %s',
                handler,
            )
