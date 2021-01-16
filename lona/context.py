import threading
import asyncio


def get_current_context_name():
    # we are running on the ioloop
    if threading.current_thread() is threading.main_thread():
        task = asyncio.Task.current_task()

        return 'Task #{}'.format(id(task))

    # we are running in a thread
    else:
        return threading.currentThread().getName()
