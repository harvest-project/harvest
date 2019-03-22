import json

import iso8601
from django.db import models

from Harvest.throttling import ThrottledRequest
from plugins.redacted.exceptions import RedactedException
from torrents.fields import InfoHashField
from torrents.models import TorrentInfo


class RedactedClientConfig(models.Model):
    username = models.TextField()
    password = models.TextField()

    login_datetime = models.DateTimeField(null=True)
    # None if not logged in, set otherwise
    cookies = models.BinaryField(null=True)
    authkey = models.TextField(null=True)
    passkey = models.TextField(null=True)

    # Set if the last login attempt failed. Use to prevent login attempt flooding. Reset manually or by user/pass change
    last_login_failed = models.BooleanField(default=False)

    def clear_login_data(self):
        self.login_datetime = None
        self.cookies = None
        self.authkey = None
        self.passkey = None

    @classmethod
    def get_locked_config(cls):
        return cls.objects.select_for_update().get()


class RedactedThrottledRequest(ThrottledRequest, models.Model):
    url = models.CharField(max_length=2048)  # Used for debugging purposes to watch what requests are going through


class RedactedTorrentGroup(models.Model):
    fetched_datetime = models.DateTimeField()
    is_deleted = models.BooleanField()

    name = models.CharField(max_length=65536)
    year = models.IntegerField()
    record_label = models.CharField(max_length=65536)
    catalog_number = models.CharField(max_length=65536)
    release_type = models.IntegerField()
    category_id = models.IntegerField()
    category_name = models.CharField(max_length=65536)
    time = models.DateTimeField()
    vanity_house = models.BooleanField()
    is_bookmarked = models.BooleanField()
    music_info = models.TextField()
    tags = models.TextField()
    wiki_body = models.TextField()
    wiki_image = models.CharField(max_length=65536)

    def update_from_redacted_dict(self, fetched_datetime, data):
        if self.id and self.id != data['id']:
            raise RedactedException('Trying to update a Redacted group with a mismatched id')
        if self.fetched_datetime and self.fetched_datetime > fetched_datetime:
            return

        self.fetched_datetime = fetched_datetime
        self.is_deleted = False

        self.id = data['id']
        self.name = data['name']
        self.year = data['year']
        self.record_label = data['recordLabel']
        self.catalog_number = data['catalogueNumber']
        self.release_type = data['releaseType']
        self.category_id = data['categoryId']
        self.category_name = data['categoryName']
        self.time = iso8601.parse_date(data['time'])
        self.vanity_house = data['vanityHouse']
        self.is_bookmarked = data['isBookmarked']
        self.music_info = json.dumps(data['musicInfo'])
        self.tags = ','.join(data['tags'])
        self.wiki_body = data['wikiBody']
        self.wiki_image = data['wikiImage']


class RedactedTorrent(models.Model):
    fetched_datetime = models.DateTimeField()
    is_deleted = models.BooleanField()

    torrent_info = models.OneToOneField(TorrentInfo, models.CASCADE, related_name='redacted_torrent')
    torrent_group = models.ForeignKey(RedactedTorrentGroup, models.PROTECT)
    info_hash = InfoHashField(db_index=True)
    media = models.CharField(max_length=64)
    format = models.CharField(max_length=64)
    encoding = models.CharField(max_length=64)
    remastered = models.BooleanField()
    remaster_year = models.IntegerField(null=True)
    remaster_title = models.CharField(max_length=65536, null=True)
    remaster_record_label = models.CharField(max_length=65536, null=True)
    remaster_catalog_number = models.CharField(max_length=65536, null=True)
    scene = models.BooleanField()
    has_log = models.BooleanField()
    has_cue = models.BooleanField()
    log_score = models.IntegerField(null=True)
    file_count = models.IntegerField()
    size = models.BigIntegerField()
    seeders = models.IntegerField()
    leechers = models.IntegerField()
    snatched = models.IntegerField()
    free_torrent = models.BooleanField()
    reported = models.BooleanField()
    time = models.DateTimeField()
    description = models.TextField()
    file_list = models.TextField()
    user_id = models.IntegerField()
    username = models.CharField(max_length=65536)

    def update_from_redacted_dict(self, torrent_info, torrent_group_id, data):
        if self.id and self.id != data['id']:
            raise RedactedException('Trying to update a Redacted torrent with a mismatched id')
        if self.fetched_datetime and self.fetched_datetime > torrent_info.fetched_datetime:
            return

        self.fetched_datetime = torrent_info.fetched_datetime
        self.is_deleted = False

        self.id = data['id']
        self.torrent_info_id = torrent_info.id
        self.torrent_group_id = torrent_group_id
        self.info_hash = data['infoHash'].lower()
        self.media = data['media']
        self.format = data['format']
        self.encoding = data['encoding']
        self.remastered = data['remastered']
        self.remaster_year = data['remasterYear']
        self.remaster_title = data['remasterTitle']
        self.remaster_record_label = data['remasterRecordLabel']
        self.remaster_catalog_number = data['remasterCatalogueNumber']
        self.scene = data['scene']
        self.has_log = data['hasLog']
        self.has_cue = data['hasCue']
        self.log_score = data['logScore']
        self.file_count = data['fileCount']
        self.size = data['size']
        self.seeders = data['seeders']
        self.leechers = data['leechers']
        self.snatched = data['snatched']
        self.free_torrent = data['freeTorrent']
        self.reported = data['reported']
        self.time = iso8601.parse_date(data['time'])
        self.description = data['description']
        self.file_list = data['fileList']
        self.user_id = data['userId']
        self.username = data['username']
