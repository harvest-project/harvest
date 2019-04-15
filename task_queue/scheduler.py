import asyncio
import signal
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.db import transaction, close_old_connections
from django.utils import timezone

from Harvest.utils import get_logger
from task_queue.models import AsyncTask
from task_queue.task_queue import TaskQueue

logger = get_logger(__name__)


class QueueExecutor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(1)
        self.current = None

    async def submit(self, fn, *args, **kwargs):
        return await asyncio.wrap_future(self.executor.submit(fn, *args, **kwargs))


class QueueScheduler:
    def __init__(self):
        self.executors = [QueueExecutor() for _ in range(settings.TASK_QUEUE_WORKERS)]
        self.shutting_down = False
        self.pending_periodic_tasks = set()
        self.executing_periodic_tasks = set()

    def _handle_shutdown_signal(self, sig_num, frame):
        self.shutting_down = True
        logger.info('Shutting down due to signal {}.', sig_num)

    async def execute_periodic_task(self, executor, task_info):
        try:
            logger.info('Executing periodic task {}.', task_info.handler_str)
            start = time.time()
            await executor.submit(task_info.handler)
            logger.info('Completed periodic task {} in {:.3f}.', task_info.handler_str, time.time() - start)
        except Exception:
            logger.exception('Exception in task {}.', task_info.handler_str)
        self.executing_periodic_tasks.remove(task_info)
        executor.current = None
        self.poll_tasks()

    async def execute_async_task(self, executor, async_task):
        self.poll_tasks()
        try:
            logger.info('Executing async task {}.', async_task.handler)
            try:
                task_info = TaskQueue.async_tasks[async_task.handler]
            except KeyError:
                raise Exception('Unable to find task with key {}.'.format(async_task.handler))
            task_args = async_task.args
            start = time.time()
            await executor.submit(task_info.handler, *task_args['args'], **task_args['kwargs'])
            async_task.status = AsyncTask.STATUS_SUCCEEDED
            logger.info('Completed async task {} in {:.3f}.', async_task.handler, time.time() - start)
        except Exception:
            async_task.status = AsyncTask.STATUS_ERRORED
            async_task.traceback = traceback.format_exc()
            logger.exception('Exception in task {}.', async_task.handler)
        async_task.completed_datetime = timezone.now()
        async_task.save()
        executor.current = None
        self.poll_tasks()

    @transaction.atomic
    def fetch_async_task(self):
        next_task = AsyncTask.objects.filter(status=AsyncTask.STATUS_PENDING).select_for_update().first()
        if next_task is None:
            raise KeyError()
        next_task.status = AsyncTask.STATUS_EXECUTING
        next_task.started_datetime = timezone.now()
        next_task.save(update_fields=('status', 'started_datetime'))
        return next_task

    def poll_tasks(self):
        while not self.shutting_down:
            free_executors = [e for e in self.executors if e.current is None]
            if not free_executors:
                logger.debug('No free executors')
                break

            try:
                task_info = self.pending_periodic_tasks.pop()
                self.executing_periodic_tasks.add(task_info)
                free_executors[0].current = asyncio.ensure_future(
                    self.execute_periodic_task(free_executors[0], task_info))
                continue
            except KeyError:
                logger.debug('No periodic tasks to be executed.')

            try:
                next_task = self.fetch_async_task()
                free_executors[0].current = asyncio.ensure_future(
                    self.execute_async_task(free_executors[0], next_task))
                continue
            except KeyError:
                logger.debug('No async tasks to be executed.')

            break

    async def periodic_task_tick(self, task_info):
        while not self.shutting_down:
            if task_info in self.executing_periodic_tasks:
                logger.debug('Skipping executing periodic task {}', task_info.handler_str)
            else:
                logger.debug('Scheduling periodic task {}.', task_info.handler_str)
                self.pending_periodic_tasks.add(task_info)
            await asyncio.sleep(task_info.interval_seconds)

    async def loop(self):
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)

        logger.info('Starting queue scheduler with {} workers.', len(self.executors))

        for periodic_task_info in TaskQueue.periodic_tasks.values():
            asyncio.ensure_future(self.periodic_task_tick(periodic_task_info))

        while not self.shutting_down:
            self.poll_tasks()
            close_old_connections()
            await asyncio.sleep(settings.TASK_QUEUE_POLL_INTERVAL)

    def run(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self.loop())
        for executor in self.executors:
            if executor.current:
                event_loop.run_until_complete(executor.current)
        logger.info('Completed shutdown.')
