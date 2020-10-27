from django.core.management.base import BaseCommand
from django.db import transaction

from Harvest.utils import get_logger
from torrents.exceptions import AlcazarNotConfiguredException
from torrents.models import AlcazarClientConfig

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Run the queue consumer"
    _type_map = {'int': int, 'float': float}

    def add_arguments(self, parser):
        parser.add_argument('--base-url', default='http://localhost:7001/')
        parser.add_argument('--token', default='')

    @transaction.atomic()
    def handle(self, *args, **options):
        try:
            config = AlcazarClientConfig.get_locked_config()
        except AlcazarNotConfiguredException:
            config = AlcazarClientConfig()

        config.base_url = options['base_url']
        config.token = options['token']
        config.save()
