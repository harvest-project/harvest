from monitoring.decorators import log_exceptions, log_successes
from torrents.alcazar_client import AlcazarClient

def force_recheck(*, torrent):
    client = AlcazarClient(timeout=AlcazarClient.TIMEOUT_LONG)
    return client.force_recheck(torrent.realm.name, torrent.info_hash)

def move_data(*, torrent, download_path):
    client = AlcazarClient(timeout=AlcazarClient.TIMEOUT_LONG)
    raise NotImplementedError()

def force_reannounce(*, torrent):
    client = AlcazarClient(timeout=AlcazarClient.TIMEOUT_LONG)
    return client.force_reannounce(torrent.realm.name, torrent.info_hash)