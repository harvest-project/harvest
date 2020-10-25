from django.db import transaction

from plugins.bibliotik import html_parser
from plugins.bibliotik.client import BibliotikClient
from plugins.bibliotik.compression import bibliotik_compress_html, bibliotik_decompress_html
from plugins.bibliotik.models import BibliotikTorrent
from plugins.bibliotik.serializers import BibliotikTorrentInfoMetadataSerializer
from trackers.models import FetchTorrentResult, BaseTracker


class BibliotikTrackerPlugin(BaseTracker):
    name = 'bibliotik'
    display_name = 'Bibliotik.me'
    torrent_info_metadata_serializer_class = BibliotikTorrentInfoMetadataSerializer
    torrents_select_related = ('torrent_info__bibliotik_torrent',)

    def fetch_torrent(self, tracker_id, fetch_torrent_file):
        client = BibliotikClient()
        torrent_html = client.get_torrent(tracker_id)
        if fetch_torrent_file:
            torrent_filename, torrent_file = client.get_torrent_file(tracker_id)
        else:
            torrent_filename, torrent_file = None, None
        return FetchTorrentResult(
            raw_response=bibliotik_compress_html(torrent_html),
            torrent_filename=torrent_filename,
            torrent_file=torrent_file,
        )

    @transaction.atomic
    def on_torrent_info_updated(self, torrent_info):
        try:
            torrent = BibliotikTorrent.objects.select_for_update().get(id=torrent_info.tracker_id)
        except BibliotikTorrent.DoesNotExist:
            torrent = BibliotikTorrent(
                id=torrent_info.tracker_id,
                torrent_info=torrent_info,
                is_deleted=False,
            )
        if torrent.fetched_datetime and torrent.fetched_datetime > torrent_info.fetched_datetime:
            return
        torrent.fetched_datetime = torrent_info.fetched_datetime
        torrent.is_deleted = torrent_info.is_deleted
        html_parser.update_torrent_from_html(torrent, bibliotik_decompress_html(bytes(torrent_info.raw_response)))
        torrent.save()
