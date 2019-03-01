from django.core.management import BaseCommand

from plugins.redacted.client import RedactedClient


class Command(BaseCommand):
    def handle(self, *args, **options):
        for _ in range(1):
            print(RedactedClient._request('index'))
