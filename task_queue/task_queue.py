import pickle
from functools import partial, wraps

from django.db import close_old_connections

from task_queue.models import AsyncTask


def db_decorator(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        finally:
            close_old_connections()

    return inner


class AsyncTaskInfo:
    def __init__(self, handler):
        self.handler = db_decorator(handler)
        self.handler_str = handler.__module__ + '.' + handler.__name__


class PeriodicTaskInfo(AsyncTaskInfo):
    def __init__(self, handler, interval_seconds):
        super().__init__(handler)
        self.interval_seconds = interval_seconds


class _TaskQueue:
    def __init__(self):
        self.async_tasks = {}
        self.periodic_tasks = {}

    def async_task(self):
        def decorator(fn):
            task_info = AsyncTaskInfo(fn)
            self.async_tasks[task_info.handler_str] = task_info
            fn.delay = partial(self._execute_async, task_info)
            return fn

        return decorator

    def periodic_task(self, interval_seconds):
        def decorator(fn):
            task_info = PeriodicTaskInfo(fn, interval_seconds)
            self.periodic_tasks[task_info.handler_str] = task_info
            fn.delay = partial(self._execute_async, task_info)
            return fn

        return decorator

    def _execute_async(self, task_info, *args, **kwargs):
        AsyncTask.objects.create(
            handler=task_info.handler_str,
            args_pickle=pickle.dumps({
                'args': args,
                'kwargs': kwargs,
            })
        )


TaskQueue = _TaskQueue()
