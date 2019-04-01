from django.core.management.base import BaseCommand
from django.db import transaction

from Harvest.utils import get_logger
from upload_studio.models import Project

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Deletes all data for a project and resets all state"

    def add_arguments(self, parser):
        parser.add_argument('project_id')

    @transaction.atomic()
    def handle(self, *args, **options):
        project = Project.objects.get(id=options['project_id'])
        project.reset()
