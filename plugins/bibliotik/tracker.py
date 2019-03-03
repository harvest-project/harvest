from plugins.bibliotik.client import BibliotikClient
from trackers.models import FetchTorrentResult


class BibliotikTrackerPlugin:
    name = 'bibliotik'
    display_name = 'Bibliotik.me'

    download_location_components = ()

    def fetch_torrent(self, tracker_id):
        client = BibliotikClient()
        torrent_html = client.get_torrent(tracker_id)
        torrent_filename, torrent_file = client.get_torrent_file(tracker_id)
        return FetchTorrentResult(
            raw_response=torrent_html,
            torrent_filename=torrent_filename,
            torrent_file=torrent_file,
        )

    def on_torrent_info_updated(self, torrent_info):
        pass

    def get_download_location_context(self, torrent_info):
        return []
