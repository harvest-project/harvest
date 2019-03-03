import string

from rest_framework.exceptions import APIException

from trackers.registry import TrackerRegistry, PluginMissingException
from trackers.utils import TorrentFileInfo


class DownloadLocationException(APIException):
    def __init__(self, detail):
        super().__init__(detail, 400)


class DownloadLocationComponent:
    def __init__(self, key, description, example):
        self.key = key
        self.description = description
        self.example = example


def get_download_location_context(torrent_file, torrent_info):
    context = {
        'torrent_file': TorrentFileInfo(torrent_file),
    }

    if torrent_info:
        context.update({
            'torrent_info': torrent_info
        })

        try:
            tracker = TrackerRegistry.get_plugin(torrent_info.realm.name, 'get_download_location_context')
            context.update(tracker.get_download_location_context(torrent_info))
        except PluginMissingException:
            pass

    return context


class DownloadLocationFormatter(string.Formatter):
    def convert_field(self, value, conversion):
        value = super().convert_field(value, conversion)
        value = value.replace('/', '_')
        return value


def format_download_path_pattern(download_path_pattern, torrent_file, torrent_info):
    context = get_download_location_context(torrent_file, torrent_info)
    try:
        download_path = DownloadLocationFormatter().format(download_path_pattern, **context)
    except Exception as exc:
        raise DownloadLocationException('Error formatting download path: {}.'.format(exc))
    if '{' in download_path or '}' in download_path:
        raise DownloadLocationException('Braces still present in pattern. Probably misformatted.')
    download_path = download_path.replace('\0', '_')
    return download_path
