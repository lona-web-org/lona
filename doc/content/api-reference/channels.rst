

Channels
========

Lona channels facilitate soft real-time communication between different
components of the server side of your application by implementing a
straightforward publish/subscribe system. They provide a means to exchange
messages among multiple views and middlewares, enabling the implementation of
multi-user features and bidirectional signaling within your application.

.. note::

    *soft* real-time means "no timing guarantees" in this case. Messages are
    guaranteed to arrive at every subscribed channel exactly once, in the
    correct order, but not at a specific time.

Each channel is associated with a topic which is represented as a string and
can be a wildcard. This allows channels to send and receive messages related
to a specific topic or a group of topics that match a particular pattern.


.. code-block:: python

    from lona import Channel


    def handle_message(message):
        topic = message.topic  # contains the topic of the sender as string
        data = message.data    # contains a dictionary of data

        print(f'{topic}: {data!r}')


    # subscribe to specific topics
    Channel('chat.rooms.lona', handle_message)
    Channel('chat.rooms.lona-releases', handle_message)


    # subscribe to wildcard topics
    Channel('chat.rooms.lona-*', handle_message)
    Channel('chat.rooms.*', handle_message)
    Channel('*', handle_message)  # subscribes to all topic, including internal topics


    # send messages to specific topics
    Channel('chat.rooms.releases').send({'lona-version': '2.0'})
    Channel('chat.rooms.lona').send()  # empty message


    # send messages to wildcard topics
    Channel('chat.rooms.lona-*').send({'lona-version': '2.0'})
    Channel('*').send({'lona-version': '2.0'})


    # explicit subscribing and unsubscribing
    channel = Channel('chat.rooms.lona')

    channel.subscribe(handle_message)
    channel.unsubscribe()


Subscribing to Topics
---------------------

To subscribe to a channel, you can either set a message handler in the
constructor of ``lona.Channel`` or use the ``lona.Channel.subscribe()`` method.
Each channel can have only one topic and one handler. Once you are subscribed,
your handler will be called with ``lona.channels.Message`` objects whenever a
matching message is sent, whether it's from your channel or another.

When using channels in conjunction with views, it is highly recommended to use
`View.subscribe </api-reference/views.html#lonaview-subscribe-topic-handler-implicit-show-true>`_
instead of directly using the channel API. By utilizing
`View.subscribe </api-reference/views.html#lonaview-subscribe-topic-handler-implicit-show-true>`_,
errors are automatically handled as 500 errors, and channel gets automatically
unsubscribed when the view closes.


Sending Messages
----------------

Messages can be sent using ``Channel.send``. ``Channel.send`` creates a shallow
copy of your message data, using
`copy.copy <https://docs.python.org/3/library/copy.html#copy.copy>`_, and then
puts the message into the global channel message queue, using
`Queue.no_wait <https://docs.python.org/3/library/queue.html#queue.Queue.put_nowait>`_,
reducing the cost of sending messages to a minimum.

.. api-doc:: lona.Channel.send


Internal Topics
---------------

Lona provides a list of internal topics that can be subscribed to in order to
receive internal events.

**lona.channels.subscribe**
    Gets sent locally whenever a channel subscribes to a topic

    .. code-block:: python

        from lona import Channel

        def handle_message(message):
            topic = message.date['topic']  # subscriber topic as string

            print(f'one user subscribed to {topic}')

        Channel('lona.channels.subscribe', handle_message)

**lona.channels.unsubscribe**
    Gets sent locally whenever a channel unsubscribes from a topic

    .. code-block:: python

        from lona import Channel

        def handle_message(message):
            topic = message.date['topic']  # subscriber topic as string

            print(f'one user unsubscribed from {topic}')

        Channel('lona.channels.unsubscribe', handle_message)


Message Broker and Task Worker
------------------------------

Lona channels follow the broker pattern, where messages sent via
``Channels.send`` are added to a global queue. The message broker threads
schedule a task for each message and for each subscribed channel to another
global queue, for the task worker threads to execute.

The separation of these two stages and queues allows for the possibility of
implementing a custom message broker with network capabilities.
This flexibility enables the integration of external systems or protocols to
handle the distribution and routing of messages across a network, expanding the
capabilities of the Lona channel system.

During startup, Lona initializes a set of message broker threads and task
worker threads. The number of threads can be configured using
``settings.MAX_CHANNEL_MESSAGE_BROKER_THREADS`` and
``settings.MAX_CHANNEL_TASK_WORKER_THREADS``. You can
specify the message broker class and the task worker class that Lona should use
for these threads using ``settings.CHANNEL_MESSAGE_BROKER_CLASS`` and
``settings.CHANNEL_TASK_WORKER_CLASS`` respectively.

Both the message broker class and the task worker class need to implement a
``run`` method, which is periodically called by the base class
``lona.channels.Worker`` with a timeout. The timeout value can be configured
using ``settings.CHANNEL_WORKER_TIMEOUT``.

**Settings:** `Threads </api-reference/settings.html#threads>`_,
`Channels </api-reference/settings.html#channels>`_


Default Message Broker
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :import: lona.channels.MessageBroker


Default Task Worker
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :import: lona.channels.TaskWorker
