import hashlib

import bencode


def get_info_hash_from_torrent(torrent_data):
    meta_info = bencode.bdecode(torrent_data)
    info = meta_info['info']
    return hashlib.sha1(bencode.bencode(info)).hexdigest()
