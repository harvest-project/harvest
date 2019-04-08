from datetime import timedelta

from django.utils import timezone

from task_queue.models import AsyncTask
from task_queue.task_queue import TaskQueue


@TaskQueue.periodic_task(3600)
def task_queue_maintenance():
    AsyncTask.objects.filter(created_datetime__lt=timezone.now() - timedelta(days=30)).delete()
