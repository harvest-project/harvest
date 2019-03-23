from rest_framework import status
from rest_framework.exceptions import APIException


class TrackerException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


class TorrentNotFoundException(TrackerException):
    status_code = status.HTTP_410_GONE
    default_detail = 'Torrent not found'
