from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import APIException

from torrents.alcazar_client import AlcazarClient, create_or_update_torrent_from_alcazar
from torrents.models import TorrentInfo, TorrentFile, Realm
from trackers.utils import get_info_hash_from_torrent


def fetch_torrent(realm, tracker, tracker_id, *, force_fetch=True):
    if not force_fetch:
        torrent_info = TorrentInfo.objects.filter(realm=realm, tracker_id=tracker_id).first()
        if torrent_info:
            return torrent_info

    fetch_datetime = timezone.now()
    fetch_torrent_result = tracker.fetch_torrent(tracker_id)
    info_hash = get_info_hash_from_torrent(fetch_torrent_result.torrent_file)
    with transaction.atomic():
        torrent_info, _ = TorrentInfo.objects.update_or_create(
            realm=realm,
            tracker_id=tracker_id,
            defaults={
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
        tracker.on_torrent_info_updated(torrent_info)
    return torrent_info


def add_torrent_from_tracker(tracker, tracker_id, download_path, *, force_fetch=True):
    try:
        realm = Realm.objects.get(name=tracker.name)
    except Realm.DoesNotExist:
        raise APIException('Realm for tracker {} not found. Please create one by adding an instance.'.format(
            tracker.name), 400)
    torrent_info = fetch_torrent(realm, tracker, tracker_id, force_fetch=force_fetch)
    client = AlcazarClient()
    added_state = client.add_torrent(realm.name, torrent_info.torrent_file.torrent_file, download_path)
    torrent, _ = create_or_update_torrent_from_alcazar(realm, torrent_info.id, added_state)
    return torrent


def add_torrent_from_file(realm, torrent_file, download_path):
    client = AlcazarClient()
    added_torrent_state = client.add_torrent(realm.name, torrent_file, download_path)
    added_torrent, _ = create_or_update_torrent_from_alcazar(realm, None, added_torrent_state)
    return added_torrent
