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
    def get_config(cls):
        return cls.objects.get()


class BibliotikThrottledRequest(ThrottledRequest, models.Model):
    url = models.CharField(max_length=2048)  # Used for debugging purposes to watch what requests are going through


class BibliotikTorrent(models.Model):
    CATEGORY_EBOOKS = 'Ebooks'
    CATEGORY_APPLICATIONS = 'Applications'
    CATEGORY_ARTICLES = 'Articles'
    CATEGORY_AUDIOBOOKS = 'Audiobooks'
    CATEGORY_COMICS = 'Comics'
    CATEGORY_JOURNALS = 'Journals'
    CATEGORY_MAGAZINES = 'Magazines'

    CATEGORY_CHOICES = (
        (CATEGORY_EBOOKS, CATEGORY_EBOOKS),
        (CATEGORY_APPLICATIONS, CATEGORY_APPLICATIONS),
        (CATEGORY_ARTICLES, CATEGORY_ARTICLES),
        (CATEGORY_AUDIOBOOKS, CATEGORY_AUDIOBOOKS),
        (CATEGORY_COMICS, CATEGORY_COMICS),
        (CATEGORY_JOURNALS, CATEGORY_JOURNALS),
        (CATEGORY_MAGAZINES, CATEGORY_MAGAZINES),
    )

    LANGUAGES = ['English', 'Irish', 'German', 'French', 'Spanish', 'Italian', 'Latin', 'Hebrew', 'Hindi', 'Japanese',
                 'Danish', 'Swedish', 'Norwegian', 'Finnish', 'Dutch', 'Russian', 'Polish', 'Portuguese', 'Greek',
                 'Catalan', 'Turkish', 'Hungarian', 'Bulgarian', 'Czech', 'Slovak', 'Serbian', 'Croatian', 'Macedonian',
                 'Ukrainian', 'Romanian', 'Korean', 'Chinese', 'Thai', 'Indonesian', 'Tagalog', 'Arabic', 'Bengali',
                 'Slovenian', 'Esperanto', 'Inuktitut', 'Tamil']

    LANGUAGE_CHOICES = tuple((l, l) for l in LANGUAGES)

    EBOOK_FORMATS = ['EPUB', 'PDF', 'MOBI', 'AZW3', 'DJVU', 'CBR', 'CHM', 'TXT']
    AUDIOBOOK_FORMATS = ['MP3', 'M4A', 'M4B']
    AUDIOBOOK_BITRATES = ['32 kbps', 'V8', '48 kbps', '64 kbps', '96 kbps', '128 kbps', 'V4', '160 kbps',
                          '192 kbps', '224 kbps', 'V2', '256 kbps', 'V0', '320 kbps']

    fetched_datetime = models.DateTimeField()
    is_deleted = models.BooleanField()

    torrent_info = models.OneToOneField(TorrentInfo, models.CASCADE, related_name='bibliotik_torrent')
    info_hash = InfoHashField(db_index=True)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, db_index=True)
    format = models.CharField(max_length=16, null=True)
    retail = models.BooleanField(default=False)
    pages = models.IntegerField(null=True)
    language = models.CharField(max_length=32, choices=LANGUAGE_CHOICES, null=True)
    isbn = models.CharField(max_length=16, null=True)
    cover_url = models.TextField(null=True)
    tags = models.TextField()
    publisher = models.TextField(null=True)
    year = models.IntegerField(null=True)
    joined_authors = models.TextField()
    authors_json = models.TextField()
    title = models.TextField()
    size = models.BigIntegerField(null=True)
