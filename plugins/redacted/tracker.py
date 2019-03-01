import json

from plugins.redacted.client import RedactedClient
from trackers.models import FetchTorrentResult


class RedactedTrackerPlugin:
    name = 'redacted'
    display_name = 'Redacted.ch'

    def fetch_torrent(self, tracker_id):
        client = RedactedClient()
        torrent_info = client.get_torrent(tracker_id)
        torrent_filename, torrent_file = client.get_torrent_file(tracker_id)
        return FetchTorrentResult(
            raw_response=json.dumps(torrent_info),
            torrent_filename=torrent_filename,
            torrent_file=torrent_file,
        )

    def on_torrent_info_updated(self, torrent_info):
        pass
