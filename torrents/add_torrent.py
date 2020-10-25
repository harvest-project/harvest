from django.db import transaction
from django.utils import timezone

from monitoring.decorators import log_exceptions, log_successes
from torrents.alcazar_client import AlcazarClient, create_or_update_torrent_from_alcazar
from torrents.download_locations import format_download_path_pattern
from torrents.exceptions import RealmNotFoundException, TorrentAlreadyExistsException
from torrents.models import TorrentInfo, TorrentFile, Realm, Torrent
from trackers.exceptions import TorrentNotFoundException
from trackers.utils import TorrentFileInfo


@transaction.atomic
def fetch_torrent(realm, tracker, tracker_id, *, force_fetch=True):
    if not force_fetch:
        torrent_info = TorrentInfo.objects.filter(realm=realm, tracker_id=tracker_id).first()
        if torrent_info:
            return torrent_info

    fetch_datetime = timezone.now()

    # After fetching, if the torrent does not exist, but we have it in the DB, mark it as deleted
    try:
        fetch_torrent_result = tracker.fetch_torrent(tracker_id)
    except TorrentNotFoundException:
        try:
            torrent_info = TorrentInfo.objects.get(realm=realm, tracker_id=tracker_id)
            torrent_info.is_deleted = True
            torrent_info.fetched_datetime = fetch_datetime
            torrent_info.save(update_fields=('fetched_datetime', 'is_deleted',))
            tracker.on_torrent_info_updated(torrent_info)
            return torrent_info
        except TorrentInfo.DoesNotExist:
            pass
        raise

    info_hash = TorrentFileInfo(fetch_torrent_result.torrent_file).info_hash
    torrent_info, _ = TorrentInfo.objects.update_or_create(
        realm=realm,
        tracker_id=tracker_id,
        defaults={
            'is_deleted': False,
            'info_hash': info_hash,
            'fetched_datetime': fetch_datetime,
            'raw_response': fetch_torrent_result.raw_response,
        },
    )
    TorrentFile.objects.update_or_create(
        torrent_info=torrent_info,
        defaults={
            'fetched_datetime': fetch_datetime,
            'torrent_filename': fetch_torrent_result.torrent_filename,
            'torrent_file': fetch_torrent_result.torrent_file,
        },
    )
    try:
        torrent = Torrent.objects.get(realm=realm, info_hash=info_hash)
        torrent.torrent_info = torrent_info
        torrent.save(update_fields=('torrent_info',))
    except Torrent.DoesNotExist:
        pass
    tracker.on_torrent_info_updated(torrent_info)
    return torrent_info


@log_exceptions('Error adding torrent {tracker_id} from {tracker.name}: {exc}.')
@log_successes('Added torrent {tracker_id} from {tracker.name} in {return.download_path},'
               ' took {time_taken:.3f} s.')
def add_torrent_from_tracker(*, tracker, tracker_id, download_path_pattern=None, force_fetch=True,
                             store_files_hook=None):
    try:
        realm = Realm.objects.get(name=tracker.name)
    except Realm.DoesNotExist:
        raise RealmNotFoundException(tracker.name)
    try:
        torrent_info = TorrentInfo.objects.get(realm=realm, tracker_id=tracker_id, is_deleted=False)
        torrent = Torrent.objects.get(realm=realm, info_hash=torrent_info.info_hash)
        raise TorrentAlreadyExistsException(torrent.client)
    except (TorrentInfo.DoesNotExist, Torrent.DoesNotExist):
        pass
    if download_path_pattern is None:
        download_path_pattern = realm.get_preferred_download_location().pattern

    client = AlcazarClient(timeout=AlcazarClient.TIMEOUT_LONG)
    torrent_info = fetch_torrent(realm, tracker, tracker_id, force_fetch=force_fetch)
    torrent_file_bytes = bytes(torrent_info.torrent_file.torrent_file)
    download_path = format_download_path_pattern(
        download_path_pattern,
        torrent_file_bytes,
        torrent_info,
    )
    if store_files_hook:
        store_files_hook(torrent_info, download_path)
    added_state = client.add_torrent(
        realm.name,
        torrent_file_bytes,
        download_path,
    )
    torrent, _ = create_or_update_torrent_from_alcazar(realm, torrent_info.id, added_state)
    return torrent


@log_exceptions('Error adding torrent file to {realm.name}: {exc}.')
@log_successes('Added torrent file to {realm.name} in {return.download_path}, took {time_taken:.3f} s.')
def add_torrent_from_file(*, realm, torrent_file, download_path_pattern=None):
    client = AlcazarClient(timeout=AlcazarClient.TIMEOUT_LONG)
    if download_path_pattern is None:
        download_path_pattern = realm.get_preferred_download_location().pattern
    download_path = format_download_path_pattern(
        download_path_pattern,
        torrent_file,
        None,
    )
    added_torrent_state = client.add_torrent(
        realm.name,
        torrent_file,
        download_path,
    )
    added_torrent, _ = create_or_update_torrent_from_alcazar(realm, None, added_torrent_state)
    return added_torrent
