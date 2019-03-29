import sys

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from Harvest.utils import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Run the queue consumer"
    _type_map = {'int': int, 'float': float}

    def add_arguments(self, parser):
        parser.add_argument('--exists-ok', default=False, action='store_true')
        parser.add_argument('username')
        parser.add_argument('password')

    def handle(self, *args, **options):
        try:
            User.objects.create_superuser(
                username=options['username'],
                email=None,
                password=options['password'],
            )
            logger.info('User {} created.', options['username'])
        except IntegrityError:
            if not options['exists_ok']:
                print('User {} already exists!'.format(options['username']))
                sys.exit(1)
