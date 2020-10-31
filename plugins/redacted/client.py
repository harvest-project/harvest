import requests
from django.utils import timezone

from Harvest.throttling import DatabaseSyncedThrottler
from Harvest.utils import get_filename_from_content_disposition, control_transaction, get_logger
from plugins.redacted.exceptions import RedactedTorrentNotFoundException, \
    RedactedRateLimitExceededException, \
    RedactedException, RedactedLoginException, RedactedArtistNotFoundException
from plugins.redacted.models import RedactedThrottledRequest, RedactedClientConfig

logger = get_logger(__name__)

HEADERS = {
    'Content-type': 'application/x-www-form-urlencoded',
    'Accept-Charset': 'utf-8',
    'User-Agent': 'Harvest'
}

DOMAIN = 'redacted.ch'


class RedactedClient:
    UPLOAD_TIMEOUT = 60

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.throttler = self.get_throttler()
        self.config = None

    @property
    def ajax_url(self):
        return 'https://{}/ajax.php'.format(DOMAIN)

    @property
    def log_url(self):
        return 'https://{}/log.php'.format(DOMAIN)

    def _ensure_keys(self, force=False):
        if not force and self.config.login_datetime:
            return

        logger.debug('Fetching authkey/passkey.')

        # Working outside of the normal __request cycling since this is a special case
        self.throttler.throttle_request(url='{}?action=index')
        index_response = requests.get(
            self.ajax_url,
            params={'action': 'index'},
            allow_redirects=False,
            timeout=self.timeout,
            headers={
                'Authorization': self.config.api_key,
                **HEADERS,
            },
        )
        if index_response.status_code != 200:
            raise RedactedLoginException('Incorrect Redacted API key or other access error.')

        self.config.last_login_failed = False
        self.config.login_datetime = timezone.now()
        self.config.authkey = index_response.json()['response']['authkey']
        self.config.passkey = index_response.json()['response']['passkey']
        self.config.save()

        logger.info('Login succeeded authkey/passkey stored.')

    def __request(self, method, url, **kwargs):
        if self.config.last_login_failed:
            logger.debug('Refusing to retry failed login attempt.')
            raise RedactedException(
                'Refusing to retry failed login attempt. Check connection settings manually.')

        logger.info('Requesting {} {}.', method, url)

        # Force authkey refresh for upload requests
        self._ensure_keys(kwargs.get('params', {}).get('action', '') == 'upload')

        kwargs.setdefault('method', method)
        kwargs.setdefault('url', url)
        kwargs.setdefault('timeout', self.timeout)

        kwargs.setdefault('headers', {})
        kwargs['headers'] = {
            'Authorization': self.config.api_key,
            **HEADERS,
            **kwargs.get('headers', {}),
        }

        if 'params' in kwargs:
            params = dict(kwargs['params'])
            kwargs['params'] = params
            if 'auth' in params and params['auth'] is None:
                params['auth'] = self.config.authkey
            if 'authkey' in params and params['authkey'] is None:
                params['authkey'] = self.config.authkey
            if 'torrent_pass' in params and params['torrent_pass'] is None:
                params['torrent_pass'] = self.config.passkey

        if 'data' in kwargs:
            data = dict(kwargs['data'])
            kwargs['data'] = data
            if 'auth' in data and data['auth'] is None:
                data['auth'] = self.config.authkey

        self.throttler.throttle_request(url='{} {}'.format(method, url))
        resp = requests.request(**kwargs)
        if resp.status_code == 302:
            self.config.last_login_failed = True
            self.config.save()
            raise RedactedLoginException('Incorrect Redacted API key or other access error.')

        return resp

    @control_transaction()
    def _request(self, method, url, **kwargs):
        try:
            self.config = RedactedClientConfig.objects.using('control').select_for_update().get()
        except RedactedClientConfig.DoesNotExist:
            raise RedactedException(
                'Client config is missing. Please configure your account through settings.')

        try:
            return self.__request(method, url, **kwargs)
        except RedactedException:
            raise
        except Exception as ex:
            raise RedactedException('Unable to perform Redacted request: {}'.format(ex))
        finally:
            self.config = None

    def request_ajax(self, action, data=None, headers=None, files=None, timeout=None, method='GET',
                     **kwargs):
        params = {
            'action': action,
            'auth': None,
        }
        params.update(kwargs)

        request_kwargs = {}
        if data is not None:
            request_kwargs['data'] = data
        if headers is not None:
            request_kwargs['headers'] = headers
        if files is not None:
            request_kwargs['files'] = files
        if timeout is not None:
            request_kwargs['timeout'] = timeout

        resp = self._request(
            method=method,
            url=self.ajax_url,
            params=params,
            allow_redirects=False,
            **request_kwargs,
        )

        try:
            data = resp.json()
            if data['status'] != 'success':
                if data['error'] == 'bad id parameter':
                    raise RedactedTorrentNotFoundException(
                        'Torrent {} not found'.format(kwargs['id']))
                elif data['error'] == 'bad hash parameter':
                    raise RedactedTorrentNotFoundException(
                        'Torrent {} not found'.format(kwargs['hash']))
                elif data['error'] == 'rate limit exceeded':
                    raise RedactedRateLimitExceededException(data)
                elif data['error'] == 'no artist found':
                    raise RedactedArtistNotFoundException(
                        'Artist {} not found'.format(kwargs.get('artistname', kwargs.get('id'))))
                raise RedactedException('Unknown Redacted API error: {}'.format(data))
            return data['response']
        except ValueError:
            if action == 'torrentlog' and resp.content == 'no payload data (empty result set)':
                return {'status': 'success', 'response': []}
            raise RedactedException('Error decoding JSON. Response text: {}'.format(
                resp.text[:30] + '...' if len(resp.text) > 27 else resp.text))

    def get_index(self):
        return self.request_ajax('index')

    def get_torrent(self, torrent_id):
        return self.request_ajax('torrent', id=torrent_id)

    def get_torrent_by_info_hash(self, info_hash):
        return self.request_ajax('torrent', hash=info_hash.upper())

    def get_torrent_group(self, group_id):
        return self.request_ajax('torrentgroup', id=group_id)

    def get_torrent_file(self, torrent_id, *, use_token=False):
        """Downloads the torrent at torrent_id using the authkey and passkey"""

        params = {
            'action': 'download',
            'id': str(torrent_id),
            'usetoken': '1' if use_token else '0',
        }

        r = self._request('GET', self.ajax_url, params=params, allow_redirects=False)
        if r.status_code == 200 and 'application/x-bittorrent' in r.headers['content-type'].lower():
            filename = get_filename_from_content_disposition(r.headers['content-disposition'])
            return filename, r.content
        else:
            raise RedactedException('Unable to fetch torrent - received {} {}'.format(
                r.status_code, r.headers['content-type']))

    def get_artist(self, artist_id=None, artist_name=None):
        if artist_id and artist_name:
            raise ValueError('Set exactly one of artist_id or artist_name')
        elif artist_id:
            kwargs = {'id': artist_id}
        elif artist_name:
            kwargs = {'artistname': artist_name}
        else:
            raise ValueError('Set exactly one of artist_id or artist_name')

        return self.request_ajax('artist', **kwargs)

    def get_site_log(self, page):
        r = self._request('GET', self.log_url, params={'page': page}, allow_redirects=False)
        if r.status_code != 200:
            raise RedactedException('Log.php returned status code {}.'.format(200))
        return r.text

    def browse(self, search_string, page, categories=None):
        categories_kwargs = None
        if categories is not None:
            categories_kwargs = {'filter_cat[{}]'.format(c): '1' for c in categories}
        return self.request_ajax(
            'browse',
            searchstr=search_string,
            page=page,
            **categories_kwargs,
        )

    def perform_upload(self, payload, torrent_file):
        payload['auth'] = None

        self.request_ajax(
            method='POST',
            action='upload',
            data=payload,
            files={
                'file_input': ('torrent.torrent', torrent_file),
            },
            headers={
                'Content-Type': None,
            },
            timeout=self.UPLOAD_TIMEOUT,
        )


    def get_user_id(self):
        return self.request_ajax('index')["id"]


    def get_snatched(self, offset, limit):
        return self.request_ajax('user_torrents', type='snatched', id=self.get_user_id(),
                                offset=str(offset), limit=str(limit))

    @classmethod
    def get_torrent_url(cls, torrent_id):
        return 'https://redacted.ch/torrents.php?torrentid={}'.format(torrent_id)

    @classmethod
    def get_torrent_group_url(cls, group_id):
        return 'https://redacted.ch/torrents.php?id={}'.format(group_id)

    @classmethod
    def get_throttler(cls):
        return DatabaseSyncedThrottler(RedactedClientConfig, RedactedThrottledRequest, 5, 10)
