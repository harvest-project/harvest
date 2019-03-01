import time

from huey import crontab
from huey.consumer import Scheduler


class IntervalSeconds:
    def __init__(self, interval):
        self.seconds = interval
        self.next_execution = time.time()

    def __call__(self, dt):
        if dt is None:
            now = time.time()
            if now >= self.next_execution:
                self.next_execution = max(now, self.next_execution + self.seconds)
                return True
        return False


class Crontab:
    def __init__(self, *args, **kwargs):
        self.crontab = crontab(*args, **kwargs)

    def __call__(self, dt):
        if dt is None:
            return False
        else:
            return self.crontab(dt)


class HarvestHueyScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        kwargs['interval'] = 1
        super().__init__(*args, **kwargs)

    def loop(self, now=None):
        super().loop(now)
        self.enqueue_periodic_tasks(None, None)
