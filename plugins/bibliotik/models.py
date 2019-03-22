import pickle
from http import cookiejar

from django.db import models

from Harvest.throttling import ThrottledRequest
from torrents.fields import InfoHashField
from torrents.models import TorrentInfo


class BibliotikClientConfig(models.Model):
    username = models.TextField()
    password = models.TextField()
    is_server_side_login_enabled = models.BooleanField()

    # When the login was performed
    login_datetime = models.DateTimeField(null=True)
    # None if not logged in, set otherwise
    cookies = models.BinaryField(null=True)

    # Set if the last login attempt failed. Use to prevent login attempt flooding. Reset manually or by user/pass change
    last_login_failed = models.BooleanField(default=False)

    def clear_login_data(self):
        self.login_datetime = None
        self.cookies = None

    @property
    def cookie_jar(self):
        jar = cookiejar.CookieJar()
        if self.cookies:
            for cookie in pickle.loads(self.cookies):
                jar.set_cookie(cookie)
        return jar

    @cookie_jar.setter
    def cookie_jar(self, jar):
        self.cookies = pickle.dumps([c for c in jar])

    @classmethod
    def get_locked_config(cls):
        return cls.objects.select_for_update().get()

    @classmethod
    def get_config(cls):
        return cls.objects.get()


class BibliotikThrottledRequest(ThrottledRequest, models.Model):
    url = models.CharField(max_length=2048)  # Used for debugging purposes to watch what requests are going through


class BibliotikTorrent(models.Model):
    CATEGORY_BOOKS = 'Ebooks'
    CATEGORY_APPLICATIONS = 'Applications'
    CATEGORY_ARTICLES = 'Articles'
    CATEGORY_AUDIOBOOKS = 'Audiobooks'
    CATEGORY_COMICS = 'Comics'
    CATEGORY_JOURNALS = 'Journals'
    CATEGORY_MAGAZINES = 'Magazines'

    CATEGORY_CHOICES = (
        (CATEGORY_BOOKS, CATEGORY_BOOKS),
        (CATEGORY_APPLICATIONS, CATEGORY_APPLICATIONS),
        (CATEGORY_ARTICLES, CATEGORY_ARTICLES),
        (CATEGORY_AUDIOBOOKS, CATEGORY_AUDIOBOOKS),
        (CATEGORY_COMICS, CATEGORY_COMICS),
        (CATEGORY_JOURNALS, CATEGORY_JOURNALS),
        (CATEGORY_MAGAZINES, CATEGORY_MAGAZINES),
    )

    LANGUAGES = ['English', 'Irish', 'German', 'French', 'Spanish', 'Italian', 'Latin', 'Japanese',
                 'Danish', 'Swedish', 'Norwegian', 'Dutch', 'Russian', 'Polish', 'Portuguese', 'Greek',
                 'Turkish', 'Hungarian', 'Korean', 'Chinese', 'Thai', 'Indonesian', 'Arabic']
    LANGUAGE_CHOICES = tuple((l, l) for l in LANGUAGES)

    EBOOK_FORMATS = ['EPUB', 'PDF', 'MOBI', 'AZW3', 'DJVU', 'CBR', 'CHM', 'TXT']

    fetched_datetime = models.DateTimeField()
    is_deleted = models.BooleanField()

    torrent_info = models.OneToOneField(TorrentInfo, models.CASCADE, related_name='bibliotik_torrent')
    info_hash = InfoHashField(db_index=True)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    format = models.CharField(max_length=16)
    retail = models.BooleanField(default=False)
    pages = models.IntegerField()
    language = models.CharField(max_length=32, choices=LANGUAGE_CHOICES)
    isbn = models.CharField(max_length=16)
    cover_url = models.TextField()
    tags = models.TextField()
    publisher = models.TextField()
    year = models.IntegerField(null=True)
    author = models.TextField()
    title = models.TextField()
    size = models.BigIntegerField()
