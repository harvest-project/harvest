import os

from rest_framework import status
from rest_framework.exceptions import APIException

from Harvest.path_utils import list_rel_files
from torrents.models import TorrentInfo
from trackers.registry import TrackerRegistry, PluginMissingException


def get_zip_download_filename_base(torrent):
    realm_name = torrent.realm.name.capitalize()
    try:
        torrent_info = torrent.torrent_info
        try:
            tracker = TrackerRegistry.get_plugin(torrent.realm.name, 'download_torrent_zip')
            return tracker.get_zip_download_basename(torrent_info)
        except (PluginMissingException, NotImplementedError):
            torrent_filename = os.path.splitext(
                os.path.basename(torrent_info.torrent_file.torrent_filename))[0]
            return f'[{torrent.realm.name.capitalize()} = {torrent_info.tracker_id}] {torrent_filename}'
    except TorrentInfo.DoesNotExist:
        return f'{realm_name} - {torrent.info_hash}'


def add_zip_download_files(zip_file, torrent):
    download_path = os.path.join(torrent.download_path, torrent.name)
    if os.path.isfile(download_path):
        zip_file.write(download_path, os.path.basename(download_path))
    elif os.path.isdir(download_path):
        for rel_file in list_rel_files(download_path):
            zip_file.write(
                os.path.join(download_path, rel_file),
                rel_file,
            )
    else:
        raise APIException(
            'Unknown source file type at {}.'.format(download_path),
            code=status.HTTP_400_BAD_REQUEST,
        )
