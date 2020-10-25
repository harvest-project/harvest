from rest_framework import status
from rest_framework.exceptions import APIException


class AlcazarNotConfiguredException(Exception):
    pass


class RealmNotFoundException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, realm_name):
        super().__init__('Realm {} not found. Please create one by adding an instance.'.format(
            realm_name))


class TorrentAlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, client):
        super().__init__('Torrent already exists and is present in client {}.'.format(client))
