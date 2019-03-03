import hashlib

import bencode


class TorrentFileInfo:
    def __init__(self, torrent_data):
        meta_info = bencode.bdecode(torrent_data)
        info = meta_info['info']
        self.name = info['name']
        self.info_hash = hashlib.sha1(bencode.bencode(info)).hexdigest()
