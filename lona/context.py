import threading
import asyncio


def current_thread_is_main_thread():
    return threading.current_thread() is threading.main_thread()


def get_current_context_name():
    # we are running on the ioloop
    if current_thread_is_main_thread():
        task = asyncio.Task.current_task()

        return 'Task #{}'.format(id(task))

    # we are running in a thread
    else:
        return threading.currentThread().getName()
