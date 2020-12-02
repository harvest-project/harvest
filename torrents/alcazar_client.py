import base64
import os
import threading
import urllib.parse

import django
import requests
from django.db import transaction
from iso8601 import iso8601
from requests import Session
from rest_framework.exceptions import APIException

from Harvest.utils import get_logger
from torrents import signals
from torrents.models import AlcazarClientConfig, Torrent
from trackers.utils import TorrentFileInfo

logger = get_logger(__name__)


def alcazar_torrent_equals(torrent, torrent_state):
    if torrent.info_hash != torrent_state['info_hash']:
        raise Exception('Comparing different info hash torrents.')

    date_added = torrent_state['date_added']

    return (
            torrent.client == torrent_state['client'] and
            torrent.status == torrent_state['status'] and
            torrent.download_path == torrent_state['download_path'] and
            torrent.name == torrent_state['name'] and
            torrent.size == torrent_state['size'] and
            torrent.downloaded == torrent_state['downloaded'] and
            torrent.uploaded == torrent_state['uploaded'] and
            torrent.download_rate == torrent_state['download_rate'] and
            torrent.upload_rate == torrent_state['upload_rate'] and
            torrent.progress == torrent_state['progress'] and
            (torrent.added_datetime == iso8601.parse_date(date_added) if date_added else None) and
            torrent.error == torrent_state['error'] and
            torrent.tracker_error == torrent_state['tracker_error']
    )


def _update_torrent_from_alcazar(torrent, torrent_state):
    if torrent.info_hash != torrent_state['info_hash']:
        raise Exception('Comparing different info hash torrents.')

    date_added = torrent_state['date_added']

    torrent.client = torrent_state['client']
    torrent.status = torrent_state['status']
    torrent.download_path = torrent_state['download_path']
    torrent.name = torrent_state['name']
    torrent.size = torrent_state['size']
    torrent.downloaded = torrent_state['downloaded']
    torrent.uploaded = torrent_state['uploaded']
    torrent.download_rate = torrent_state['download_rate']
    torrent.upload_rate = torrent_state['upload_rate']
    torrent.progress = torrent_state['progress']
    torrent.added_datetime = iso8601.parse_date(date_added) if date_added else None
    torrent.error = torrent_state['error']
    torrent.tracker_error = torrent_state['tracker_error']


def update_torrent_from_alcazar(torrent, torrent_state):
    if alcazar_torrent_equals(torrent, torrent_state):
        return False
    prev_progress = torrent.progress
    _update_torrent_from_alcazar(torrent, torrent_state)
    torrent.save()
    # Dispatch relevant signals
    signals.torrent_updated.send_robust(None, torrent=torrent)
    if prev_progress != 1 and torrent.progress == 1:
        signals.torrent_finished.send_robust(None, torrent=torrent)
    return True


def create_or_update_torrent_from_alcazar(realm, torrent_info_id, torrent_state):
    try:
        with transaction.atomic():
            torrent = Torrent(
                realm=realm,
                torrent_info_id=torrent_info_id,
                info_hash=torrent_state['info_hash'],
            )
            update_torrent_from_alcazar(torrent, torrent_state)
            torrent.save()
            signals.torrent_added.send_robust(None, torrent=torrent)
            return torrent, True
    except django.db.utils.IntegrityError:
        logger.info('IntegrityError creating torrent, it must have popped up. Retrieving existing.')
        torrent = Torrent.objects.get(realm=realm, info_hash=torrent_state['info_hash'])

        if torrent.torrent_info_id is None and torrent.torrent_info_id != torrent_info_id:
            logger.warning('Discovered unlinked torrent {}, linking to {}.', torrent.info_hash, torrent_info_id)
            torrent.torrent_info_id = torrent_info_id
            torrent.save()
            signals.torrent_updated.send_robust(None, torrent)

        update_torrent_from_alcazar(torrent, torrent_state)
        return torrent, False


class AlcazarRemoteException(APIException):
    def __init__(self, message, response=None):
        self.status_code = 500
        if response is not None and response.status_code in {400, 404, 409}:  # Exceptions that we forward in our API
            self.status_code = response.status_code
        super().__init__(message)


class AlcazarClient:
    TIMEOUT_LONG = 60
    TIMEOUT_SHORT = 20

    _thread_local_storage = threading.local()

    def __init__(self, timeout=TIMEOUT_SHORT):
        self.config = AlcazarClientConfig.get_config()
        self.timeout = timeout

    @property
    def _session(self):
        session = getattr(self._thread_local_storage, '_alcazar_session', None)
        if session is None:
            session = Session()
            self._thread_local_storage._alcazar_session = session
        return session

    def _request(self, method, endpoint, *args, **kwargs):
        kwargs.setdefault('timeout', self.timeout)

        try:
            resp = self._session.request(method, self._get_url(endpoint), *args, **kwargs)
        except requests.exceptions.ConnectionError:
            raise AlcazarRemoteException('Error connecting to Alcazar. Please check if it is running and connectable.')

        try:
            data = resp.json()
        except ValueError:
            raise AlcazarRemoteException('Alcazar returned non-JSON, code {}'.format(resp.status_code), resp)

        if resp.status_code == 200:
            return data
        else:
            if 'detail' in data:
                raise AlcazarRemoteException('Alcazar returned error: {}'.format(data['detail']), resp)
            raise AlcazarRemoteException('Alcazar returned non-200: {}'.format(data), resp)

    def _get_url(self, endpoint):
        return urllib.parse.urljoin(self.config.base_url, endpoint)

    def pop_update_batch(self, limit):
        return self._request('POST', '/pop_update_batch', params={'limit': limit})

    def ping(self):
        return self._request('GET', '/ping')

    def add_torrent(self, realm_name, torrent_file, download_path):
        name = None
        if self.config.unify_single_file_torrents:
            torrent_file_info = TorrentFileInfo(torrent_file)
            if torrent_file_info.is_multifile:
                name = os.path.basename(download_path)
                download_path = os.path.dirname(download_path)

        return self._request('POST', '/torrents/{}'.format(realm_name), json={
            'torrent': base64.b64encode(torrent_file).decode(),
            'download_path': download_path,
            'name': name,
        })

    def delete_torrent(self, realm_name, info_hash):
        return self._request('DELETE', '/torrents/{}/{}'.format(realm_name, info_hash))

    def get_config(self):
        return self._request('GET', '/config')

    def save_config(self, config):
        return self._request('PUT', '/config', json=config)

    def get_clients(self):
        return self._request('GET', '/clients')

    def add_client(self, client_data):
        return self._request('POST', '/clients', json=client_data)

    def force_recheck(self, realm_name, info_hash):
        return self._request('GET', '/torrents/force_recheck/{}/{}'.format(realm_name, info_hash))
    
    def force_reannounce(self, realm_name, info_hash):
        return self._request('GET', '/torrents/force_reannounce/{}/{}'.format(realm_name, info_hash))

    def move_data(self, realm_name, info_hash, download_path):
        pass
