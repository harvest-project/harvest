import logging
import time
import traceback
from functools import wraps

from monitoring.models import LogEntry, ComponentStatus


def format_message(message, args, kwargs):
    try:
        return message.format(*args, **kwargs)
    except Exception as exc:
        return '{} Error formatting message: {}.'.format(message, exc)


class log_exceptions:
    def __init__(self, message):
        self.message = message

    def __call__(self, fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                kwargs['exc'] = exc
                LogEntry.exception(format_message(self.message, args, kwargs))
                raise

        return inner


class log_successes:
    def __init__(self, message, level=logging.INFO):
        self.message = message
        self.level = level

    def __call__(self, fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            start = time.time()
            result = fn(*args, **kwargs)
            kwargs['time_taken'] = time.time() - start
            kwargs['return'] = result
            LogEntry.log(self.level, format_message(self.message, args, kwargs))
            return result

        return inner


class update_component_status:
    def __init__(self, name, success_message=None, error_message=None):
        self.name = name
        self.success_message = success_message
        self.error_message = error_message

    def __call__(self, fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            try:
                start = time.time()
                result = fn(*args, **kwargs)
                if self.success_message:
                    kwargs['time_taken'] = time.time() - start
                    ComponentStatus.update_status(
                        self.name,
                        ComponentStatus.STATUS_GREEN,
                        format_message(self.success_message, args, kwargs),
                    )
                return result
            except Exception:
                if self.error_message:
                    ComponentStatus.update_status(
                        self.name,
                        ComponentStatus.STATUS_RED,
                        format_message(self.error_message, args, kwargs),
                        traceback.format_exc(),
                    )
                raise

        return inner
