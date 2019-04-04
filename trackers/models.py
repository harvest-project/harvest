class FetchTorrentResult:
    def __init__(self, raw_response, torrent_filename, torrent_file):
        if not isinstance(raw_response, bytes):
            raise Exception('raw_response must contain a bytes instance')
        self.raw_response = raw_response
        self.torrent_filename = torrent_filename
        self.torrent_file = torrent_file


class BaseTracker:
    name = None
    display_name = None
    torrent_info_metadata_serializer = None
    download_location_components = ()

    def on_torrent_info_updated(self, torrent_info):
        pass

    def get_download_location_context(self, torrent_info):
        return []

    def get_zip_download_basename(self, torrent_info):
        raise NotImplementedError()
