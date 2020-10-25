import json

from django.db import transaction

from plugins.redacted.client import RedactedClient
from plugins.redacted.models import RedactedTorrentGroup, RedactedTorrent
from plugins.redacted.serializers import RedactedTorrentInfoMetadataSerializer
from torrents.download_locations import DownloadLocationComponent
from trackers.models import FetchTorrentResult, BaseTracker


class RedactedTrackerPlugin(BaseTracker):
    name = 'redacted'
    display_name = 'Redacted.ch'
    torrent_info_metadata_serializer_class = RedactedTorrentInfoMetadataSerializer
    torrents_select_related = ('torrent_info__redacted_torrent', 'torrent_info__redacted_torrent__torrent_group')

    download_location_components = (
        DownloadLocationComponent(
            '{redacted_group.id}',
            'ID of the torrent group in Redacted',
            '34678',
        ),
        DownloadLocationComponent(
            '{redacted_group.year}',
            'Year of the torrent group in Redacted',
            '1984',
        ),
        DownloadLocationComponent(
            '{redacted_torrent.id}',
            'ID of the torrent in Redacted',
            '976613',
        ),
        DownloadLocationComponent(
            '{redacted_torrent.media}',
            'Media name of the torrent',
            'CD',
        ),
        DownloadLocationComponent(
            '{redacted_torrent.format}',
            'File format of the files',
            'FLAC',
        ),
        DownloadLocationComponent(
            '{redacted_torrent.encoding}',
            'Encoding of the files',
            'Lossless',
        ),
        DownloadLocationComponent(
            '{redacted_torrent.remastered}',
            'Whether the torrent is a remaster',
            'True',
        ),
        DownloadLocationComponent(
            '{redacted_torrent.remaster_year}',
            'Remaster year of the torrent',
            '2007',
        ),
        DownloadLocationComponent(
            '{redacted_torrent.remaster_title}',
            'Remaster title of the torrent',
            'Remastered',
        ),
        DownloadLocationComponent(
            '{redacted_torrent.remaster_record_label}',
            'Record label of the remaster',
            'Polydor',
        ),
        DownloadLocationComponent(
            '{redacted_torrent.remaster_catalog_number}',
            'Catalog number of the remaster',
            '537 179-2',
        ),
        DownloadLocationComponent(
            '{redacted_torrent.scene}',
            'Whether the torrent is a scene release',
            'False',
        ),
    )

    def fetch_torrent(self, tracker_id, fetch_torrent_file=True):
        client = RedactedClient()
        torrent_info = client.get_torrent(tracker_id)
        if fetch_torrent_file:
            torrent_filename, torrent_file = client.get_torrent_file(tracker_id)
        else:
            torrent_filename, torrent_file = None, None
        return FetchTorrentResult(
            raw_response=json.dumps(torrent_info).encode(),
            torrent_filename=torrent_filename,
            torrent_file=torrent_file,
        )

    @transaction.atomic
    def on_torrent_info_updated(self, torrent_info):
        parsed_data = json.loads(bytes(torrent_info.raw_response).decode())

        try:
            torrent_group = RedactedTorrentGroup.objects.select_for_update().get(id=parsed_data['group']['id'])
        except RedactedTorrentGroup.DoesNotExist:
            torrent_group = RedactedTorrentGroup()
        torrent_group.update_from_redacted_dict(
            torrent_info.fetched_datetime,
            parsed_data['group'],
        )
        torrent_group.save()

        try:
            torrent = RedactedTorrent.objects.select_for_update().get(id=parsed_data['torrent']['id'])
        except RedactedTorrent.DoesNotExist:
            torrent = RedactedTorrent()
        torrent.update_from_redacted_dict(
            torrent_info,
            torrent_group.id,
            parsed_data['torrent'],
        )
        torrent.save()

    def get_download_location_context(self, torrent_info):
        try:
            torrent = torrent_info.redacted_torrent
            return {
                'redacted_torrent': torrent,
                'redacted_group': torrent.torrent_group,
            }
        except RedactedTorrent.DoesNotExist:
            return {}
