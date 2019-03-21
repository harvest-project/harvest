from rest_framework.exceptions import APIException


class TrackerException(APIException):
    status_code = 400


class TorrentNotFoundException(TrackerException):
    status_code = 404
    default_detail = 'Torrent not found'
