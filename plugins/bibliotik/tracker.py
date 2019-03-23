from django.db import transaction

from plugins.bibliotik import html_parser
from plugins.bibliotik.client import BibliotikClient
from plugins.bibliotik.models import BibliotikTorrent
from trackers.models import FetchTorrentResult, BaseTracker


class BibliotikTrackerPlugin(BaseTracker):
    name = 'bibliotik'
    display_name = 'Bibliotik.me'

    def fetch_torrent(self, tracker_id):
        client = BibliotikClient()
        torrent_html = client.get_torrent(tracker_id)
        torrent_filename, torrent_file = client.get_torrent_file(tracker_id)
        return FetchTorrentResult(
            raw_response=torrent_html,
            torrent_filename=torrent_filename,
            torrent_file=torrent_file,
        )

    @transaction.atomic
    def on_torrent_info_updated(self, torrent_info):
        # try:
        #     torrent = BibliotikTorrent.objects.select_for_update().get(id=torrent_info.tracker_id)
        # except BibliotikTorrent.DoesNotExist:
        #     torrent = BibliotikTorrent()
        # html_parser.update_torrent_from_html(torrent, torrent_info.raw_response)
        # torrent.save()
        pass
