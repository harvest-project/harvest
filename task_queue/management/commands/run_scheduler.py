import asyncio

from django.core.management.base import BaseCommand

from Harvest.utils import get_logger
from task_queue.scheduler import QueueScheduler

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Run the queue consumer"

    def handle(self, *args, **options):
        QueueScheduler().run()
