from django.core.management import BaseCommand
from django.db import transaction

from Harvest.utils import qs_chunks
from torrents.models import TorrentInfo, Realm
from trackers.registry import TrackerRegistry


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('tracker')

    def handle(self, *args, **options):
        bibliotik = TrackerRegistry.get_plugin(options['tracker'])
        try:
            realm = Realm.objects.get(name=options['tracker'])
        except Realm.DoesNotExist:
            print('Realm does not exist.')
            return

        for ti_batch in qs_chunks(TorrentInfo.objects.filter(realm=realm), 1000):
            print('Process batch')
            with transaction.atomic():
                for ti in ti_batch:
                    print('Parsing {} / {}'.format(ti.id, ti.tracker_id))
                    bibliotik.on_torrent_info_updated(ti)
