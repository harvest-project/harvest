from torrents.alcazar_client import AlcazarClient


def remove_torrent(torrent):
    client = AlcazarClient()
    client.delete_torrent(torrent.realm.name, torrent.info_hash)
