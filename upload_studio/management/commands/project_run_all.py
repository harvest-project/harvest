from django.core.management.base import BaseCommand
from django.db import transaction

from Harvest.utils import get_logger
from upload_studio.steps_runner import StepsRunner

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Run all steps on an upload studio project"

    def add_arguments(self, parser):
        parser.add_argument('project_id')

    @transaction.atomic()
    def handle(self, *args, **options):
        runner = StepsRunner(options['project_id'])
        runner.run_all()
