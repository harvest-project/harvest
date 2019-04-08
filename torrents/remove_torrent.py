from monitoring.decorators import log_exceptions, log_successes
from torrents.alcazar_client import AlcazarClient


@log_exceptions('Error removing torrent {torrent.name} from {torrent.realm.name}: {exc}.')
@log_successes('Removed torrent {torrent.name} from {torrent.realm.name}.')
def remove_torrent(*, torrent):
    client = AlcazarClient(timeout=AlcazarClient.TIMEOUT_LONG)
    client.delete_torrent(torrent.realm.name, torrent.info_hash)
