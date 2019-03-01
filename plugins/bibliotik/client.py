import logging

import requests
from django.db import transaction
from django.utils import timezone

from Harvest.throttling import DatabaseSyncedThrottler
from Harvest.utils import get_filename_from_content_disposition
from plugins.bibliotik.exceptions import BibliotikException, BibliotikLoginException
from plugins.bibliotik.models import BibliotikThrottledRequest, BibliotikClientConfig

logger = logging.getLogger(__name__)

HEADERS = {
    'Content-type': 'application/x-www-form-urlencoded',
    'Accept-Charset': 'utf-8',
    'User-Agent': 'Harvest'
}

DOMAIN = 'bibliotik.me'


class BibliotikClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = HEADERS
        self.throttler = DatabaseSyncedThrottler(BibliotikThrottledRequest, 5, 10)
        self.config = None

    @property
    def index_url(self):
        return 'https://{}/'.format(DOMAIN)

    @property
    def torrents_url(self):
        return 'https://{}/torrents/'.format(DOMAIN)

    @property
    def login_url(self):
        return self.index_url

    def get_torrent_url(self, torrent_id):
        return 'https://{}/torrents/{}'.format(DOMAIN, torrent_id)

    def get_torrent_file_url(self, torrent_id):
        return 'https://{}/torrents/{}/download'.format(DOMAIN, torrent_id)

    def _test_cookies(self, jar):
        # No cookies can't possibly work
        if len(jar) == 0:
            logger.debug('Offered 0 cookies, not working.')
            return False
        resp = requests.get(self.torrents_url, cookies=jar)
        return resp.status_code == 200

    def accept_cookies_if_ok(self, jar):
        # If we're in a transaction, we can lose login/throttling data due to outside exceptions
        if not transaction.get_autocommit():
            raise BibliotikException('You cannot make a Bibliotik request inside a transaction.')

        with transaction.atomic():
            config = BibliotikClientConfig.get_locked_config()

            logger.debug('Trying if new cookies offered work.')

            if self._test_cookies(jar):
                logger.info('New cookies offered work. Saving and returning.')
                config.cookie_jar = jar
                config.login_datetime = timezone.now()
                config.last_login_failed = False
                config.save()
                return config

            logger.debug('Trying to see if our cookies work.')

            if config.cookies and self._test_cookies(config.cookie_jar):
                logger.debug('Our cookies work, nothing to do.')
                return config

            logger.debug('No cookies work. Clearing login data.')
            config.clear_login_data()
            config.save()
            return config

    def _login(self):
        if not self.config.is_server_side_login_enabled:
            raise BibliotikException('Server requires login, but server-side login is disabled.')

        logger.debug('Attempting login with username {}'.format(self.config.username))

        if self.config.last_login_failed:
            logger.debug('Refusing to retry failed login attempt.')
            raise BibliotikException('Refusing to retry failed login attempt.')

        # Mark login as failed in order to prevent future tries if the code crashes
        self.config.last_login_failed = True
        self.config.save()

        data = {
            'username': self.config.username,
            'password': self.config.password,
            'keeplogged': 1,
            'login': 'Log In!',
        }
        # Login is not subject to the normal API rate limiting
        r = self.session.post(self.login_url, data=data, allow_redirects=False)
        if r.status_code != 302:
            logger.debug('Login failed, returned status {}'.format(r.status_code))

            if 'Wrong username/password.' in r.text:
                logger.debug('Login failed: incorrect username/password.')
                raise BibliotikLoginException('Incorrect Bibliotik username/password.')
            else:
                logger.debug('Login failed: unknown reason')
                raise BibliotikLoginException('Unknown error logging in.')

        self.config.last_login_failed = False
        self.config.login_datetime = timezone.now()
        self.config.cookie_jar = self.session.cookies
        self.config.save()

        logger.info('Login succeeded with username {}, credentials stored'.format(self.config.username))

    def __request(self, method, url, **kwargs):
        logger.info('Requesting {} {}'.format(method, url))

        if self.config.cookies:
            logger.debug('Found cached login credentials')

            self.session.cookies = self.config.cookie_jar

            self.throttler.throttle_request(url='{} {}'.format(method, url))
            resp = self.session.request(method, url, **kwargs)

            # If not logged in, try to log in
            if resp.status_code == 401:
                logger.debug('Login credentials did not work, attempting login.')

                # Clear login credentials that didn't work
                self.config.clear_login_data()
                self.config.save()

                self._login()

                self.throttler.throttle_request(url='{} {}'.format(method, url))
                resp = self.session.request(method, url, **kwargs)
                resp.raise_for_status()
        else:
            logger.debug('No login credentials found, attempting fresh login')
            self._login()

            self.throttler.throttle_request(url='{} {}'.format(method, url))
            resp = self.session.request(method, url, **kwargs)
            if resp.status_code == 401:
                raise BibliotikException('API returned redirect after fresh login')
            resp.raise_for_status()

        return resp

    def _request(self, method, url, **kwargs):
        # If we're in a transaction, we can lose login/throttling data due to outside exceptions
        if not transaction.get_autocommit():
            raise BibliotikException('You cannot make a Bibliotik request inside a transaction.')

        # Open transaction, commit regardless of exceptions and rethrow if any
        with transaction.atomic():
            try:
                self.config = BibliotikClientConfig.get_locked_config()
            except BibliotikClientConfig.DoesNotExist:
                raise BibliotikException('Client config is missing. Please configure your account through settings.')

            try:
                return self.__request(method, url, **kwargs)
            except Exception as exc:
                request_exception = exc

            self.config = None

        raise BibliotikException('Unable to fetch torrent data from Bibliotik: {}'.format(
            request_exception)) from request_exception

    def get_index(self):
        r = self._request('GET', self.index_url, allow_redirects=False)
        return r.text

    def get_torrent(self, torrent_id):
        r = self._request('GET', self.get_torrent_url(torrent_id), allow_redirects=False)
        return r.text

    def get_torrent_file(self, torrent_id):
        """Downloads the torrent at torrent_id using the authkey and passkey"""

        r = self._request('GET', self.get_torrent_file_url(torrent_id), allow_redirects=False)
        if 'application/x-bittorrent' in r.headers['content-type'].lower():
            filename = get_filename_from_content_disposition(r.headers['content-disposition'])
            return filename, r.content
        else:
            raise BibliotikException('Unable to fetch torrent - received {} {}'.format(
                r.status_code, r.headers['content-type']))
