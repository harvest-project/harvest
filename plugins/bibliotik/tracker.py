from plugins.bibliotik.client import BibliotikClient
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
