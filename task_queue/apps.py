from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class TaskQueueConfig(AppConfig):
    name = 'task_queue'

    def ready(self):
        autodiscover_modules('tasks')
