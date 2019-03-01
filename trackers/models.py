class FetchTorrentResult:
    def __init__(self, raw_response, torrent_filename, torrent_file):
        self.raw_response = raw_response
        self.torrent_filename = torrent_filename
        self.torrent_file = torrent_file
