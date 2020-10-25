import html

import iso8601
from django.db import models

from Harvest.throttling import ThrottledRequest
from plugins.redacted.exceptions import RedactedException
from plugins.redacted.utils import get_joined_artists
from torrents.fields import InfoHashField
from torrents.models import TorrentInfo


class RedactedClientConfig(models.Model):
    api_key = models.TextField()
    announce_url = models.TextField()

    login_datetime = models.DateTimeField(null=True)
    authkey = models.TextField(null=True)
    passkey = models.TextField(null=True)

    # Set if the last login attempt failed. Use to prevent login attempt flooding.
    # Reset manually or by user/pass change
    last_login_failed = models.BooleanField(default=False)


class RedactedThrottledRequest(ThrottledRequest, models.Model):
    url = models.CharField(
        max_length=2048)  # Used for debugging purposes to watch what requests are going through


class RedactedTorrentGroup(models.Model):
    RELEASE_TYPE_ALBUM = 1
    RELEASE_TYPE_SOUNDTRACK = 3
    RELEASE_TYPE_EP = 5
    RELEASE_TYPE_ANTHOLOGY = 6
    RELEASE_TYPE_COMPILATION = 7
    RELEASE_TYPE_SINGLE = 9
    RELEASE_TYPE_LIVE_ALBUM = 11
    RELEASE_TYPE_REMIX = 13
    RELEASE_TYPE_BOOTLEG = 14
    RELEASE_TYPE_INTERVIEW = 15
    RELEASE_TYPE_MIXTAPE = 16
    RELEASE_TYPE_DEMO = 17
    RELEASE_TYPE_CONCERT_RECORDING = 18
    RELEASE_TYPE_DJ_MIX = 19
    RELEASE_TYPE_UNKNOWN = 21

    fetched_datetime = models.DateTimeField(db_index=True)
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
    music_info = models.JSONField(null=True)
    tags = models.TextField()
    wiki_body = models.TextField()
    wiki_image = models.CharField(max_length=65536)

    def __str__(self):
        return 'RedactedTorrentGroup ({})'.format(self.name)

    @property
    def joined_artists(self):
        if self.music_info is None:
            return None
        return get_joined_artists(self.music_info)

    def update_from_redacted_dict(self, fetched_datetime, data):
        if self.id and self.id != data['id']:
            raise RedactedException('Trying to update a Redacted group with a mismatched id')
        if self.fetched_datetime and self.fetched_datetime > fetched_datetime:
            return

        self.fetched_datetime = fetched_datetime
        self.is_deleted = False

        self.id = data['id']
        self.name = html.unescape(data['name'])
        self.year = data['year']
        self.record_label = html.unescape(data['recordLabel'])
        self.catalog_number = html.unescape(data['catalogueNumber'])
        self.release_type = data['releaseType']
        self.category_id = data['categoryId']
        self.category_name = html.unescape(data['categoryName'])
        self.time = iso8601.parse_date(data['time'])
        self.vanity_house = data['vanityHouse']
        self.is_bookmarked = data['isBookmarked']
        self.music_info = data['musicInfo']
        self.tags = ','.join(data['tags'])
        self.wiki_body = data['wikiBody']
        self.wiki_image = data['wikiImage']

    def ensure_artists_created(self):
        if not self.music_info:
            return
        for artists in self.music_info.values():
            for artist in artists:
                RedactedArtist.objects.get_or_create(
                    id=artist['id'],
                    defaults={
                        'name': artist['name'],
                        'is_deleted': False,
                    },
                )


class RedactedTorrent(models.Model):
    FORMAT_MP3 = 'MP3'
    FORMAT_FLAC = 'FLAC'
    FORMAT_AAC = 'AAC'
    FORMAT_AC3 = 'AC3'
    FORMAT_DTS = 'DTS'
    FORMAT_CHOICES = (
        (FORMAT_MP3, FORMAT_MP3),
        (FORMAT_FLAC, FORMAT_FLAC),
        (FORMAT_AAC, FORMAT_AAC),
        (FORMAT_AC3, FORMAT_AC3),
        (FORMAT_DTS, FORMAT_DTS),
    )

    MEDIA_CD = 'CD'
    MEDIA_DVD = 'DVD'
    MEDIA_VINYL = 'Vinyl'
    MEDIA_SOUNDBOARD = 'Soundboard'
    MEDIA_SACD = 'SACD'
    MEDIA_DAT = 'DAT'
    MEDIA_CASSETTE = 'Cassette'
    MEDIA_WEB = 'WEB'
    MEDIA_BLU_RAY = 'Blu-Ray'
    MEDIA_CHOICES = (
        (MEDIA_CD, MEDIA_CD),
        (MEDIA_DVD, MEDIA_DVD),
        (MEDIA_VINYL, MEDIA_VINYL),
        (MEDIA_SOUNDBOARD, MEDIA_SOUNDBOARD),
        (MEDIA_SACD, MEDIA_SACD),
        (MEDIA_DAT, MEDIA_DAT),
        (MEDIA_CASSETTE, MEDIA_CASSETTE),
        (MEDIA_WEB, MEDIA_WEB),
        (MEDIA_BLU_RAY, MEDIA_BLU_RAY),
    )

    ENCODING_192 = '192'
    ENCODING_APS = 'APS (VBR)'
    ENCODING_V2 = 'V2 (VBR)'
    ENCODING_V1 = 'V1 (VBR)'
    ENCODING_256 = '256'
    ENCODING_APX = 'APX (VBR)'
    ENCODING_V0 = 'V0 (VBR)'
    ENCODING_320 = '320'
    ENCODING_LOSSLESS = 'Lossless'
    ENCODING_24BIT_LOSSLESS = '24bit Lossless'
    ENCODING_OTHER = 'Other'
    ENCODING_CHOICES = (
        (ENCODING_192, ENCODING_192),
        (ENCODING_APS, ENCODING_APS),
        (ENCODING_V2, ENCODING_V2),
        (ENCODING_V1, ENCODING_V1),
        (ENCODING_256, ENCODING_256),
        (ENCODING_APX, ENCODING_APX),
        (ENCODING_V0, ENCODING_V0),
        (ENCODING_320, ENCODING_320),
        (ENCODING_LOSSLESS, ENCODING_LOSSLESS),
        (ENCODING_24BIT_LOSSLESS, ENCODING_24BIT_LOSSLESS),
        (ENCODING_OTHER, ENCODING_OTHER),
    )

    fetched_datetime = models.DateTimeField(db_index=True)
    is_deleted = models.BooleanField()

    torrent_info = models.OneToOneField(TorrentInfo, models.CASCADE,
                                        related_name='redacted_torrent')
    torrent_group = models.ForeignKey(RedactedTorrentGroup, models.PROTECT)
    info_hash = InfoHashField(db_index=True)
    media = models.CharField(max_length=64, choices=MEDIA_CHOICES)
    format = models.CharField(max_length=64, choices=FORMAT_CHOICES)
    encoding = models.CharField(max_length=64, choices=ENCODING_CHOICES)
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

    def __str__(self):
        return 'RedactedTorrent ({})'.format(self.id)

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
        self.remaster_title = html.unescape(data['remasterTitle'])
        self.remaster_record_label = html.unescape(data['remasterRecordLabel'])
        self.remaster_catalog_number = html.unescape(data['remasterCatalogueNumber'])
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


class RedactedArtist(models.Model):
    fetched_datetime = models.DateTimeField(null=True, db_index=True)
    is_deleted = models.BooleanField()

    name = models.CharField(null=True, max_length=65536)
    image = models.CharField(null=True, max_length=65536)
    body = models.TextField(null=True)
    vanity_house = models.BooleanField(null=True)
    tags = models.JSONField(null=True)
    similar_artists = models.JSONField(null=True)
    statistics = models.JSONField(null=True)
    torrent_groups = models.JSONField(null=True)
    requests = models.JSONField(null=True)

    def __str__(self):
        return 'RedactedArtist ({})'.format(self.name)

    def update_from_redacted_dict(self, fetched_datetime, data):
        if self.id and self.id != data['id']:
            raise RedactedException('Trying to update a Redacted artist with a mismatched id')
        if self.fetched_datetime and self.fetched_datetime > fetched_datetime:
            return

        self.fetched_datetime = fetched_datetime
        self.is_deleted = False

        self.id = data['id']
        self.name = html.unescape(data['name'])
        self.image = data['image']
        self.body = data['body']
        self.vanity_house = data['vanityHouse']
        self.tags = data['tags']
        self.similar_artists = data['similarArtists']
        self.statistics = data['statistics']
        self.torrent_groups = data['torrentgroup']
        self.requests = data['requests']

    def get_aliases(self):
        aliases = {}
        for torrent_group in self.torrent_groups:
            for artist in torrent_group['artists']:
                aliases[artist['aliasid']] = artist['name']
            for artists in torrent_group['extendedArtists'].values():
                for artist in artists:
                    aliases[artist['aliasid']] = artist['name']
        return aliases


class RedactedRequestCacheEntry(models.Model):
    fetched_datetime = models.DateTimeField()
    action = models.CharField(max_length=128)
    kwargs_json = models.CharField(max_length=65536)
    response_json = models.TextField()

    class Meta:
        unique_together = (('action', 'kwargs_json'),)
