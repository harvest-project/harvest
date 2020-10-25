from django.core.management import BaseCommand
from django.db import transaction

from torrents.alcazar_client import AlcazarRemoteException
from torrents.models import Realm, Torrent
from torrents.remove_torrent import remove_torrent


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('realm')
        parser.add_argument('message_pattern')

    def handle(self, *args, **options):
        try:
            realm = Realm.objects.get(name=options['realm'])
        except Realm.DoesNotExist:
            print('Realm does not exist.')
            return

        torrents = list(Torrent.objects.filter(
            realm=realm,
            tracker_error__icontains=options['message_pattern']
        ))

        for torrent in torrents:
            print(torrent.name)
            print('  ', torrent.tracker_error)

        input('Matched {} torrents for deletion. Continue?'.format(len(torrents)))

        for torrent in torrents:
            print('Deleting', torrent.name)
            with transaction.atomic():
                torrent.delete()
                try:
                    remove_torrent(torrent=torrent)
                except AlcazarRemoteException as exc:
                    if exc.status_code == 404:
                        print('Torrent not present in Alcazar.'
                              'It was deleted from the DB, but please check whether '
                              'sync is running properly.')
                    else:
                        raise
                print('Successfully deleted', torrent.name)
