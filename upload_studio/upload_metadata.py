from rest_framework import serializers


class MusicMetadata:
    # Currently matching the settings in Gazelle
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

    def __init__(self, title=None, edition_year=None, edition_title=None, edition_record_label=None,
                 edition_catalog_number=None, format=None, media=None, encoding=None, torrent_name=None,
                 torrent_info_hash=None, additional_data=None):
        self.title = title
        self.edition_year = edition_year
        self.edition_title = edition_title
        self.edition_record_label = edition_record_label
        self.edition_catalog_number = edition_catalog_number

        self.format = format
        self.media = media
        self.encoding = encoding

        self.torrent_name = torrent_name
        self.torrent_info_hash = torrent_info_hash
        self.additional_data = additional_data

    @property
    def format_is_lossy(self):
        return self.format != MusicMetadata.FORMAT_FLAC


class MusicMetadataSerializer(serializers.Serializer):
    title = serializers.CharField(allow_null=True, allow_blank=True)
    edition_year = serializers.IntegerField(allow_null=True)
    edition_title = serializers.CharField(allow_null=True, allow_blank=True)
    edition_record_label = serializers.CharField(allow_null=True, allow_blank=True)
    edition_catalog_number = serializers.CharField(allow_null=True, allow_blank=True)

    format = serializers.CharField(allow_null=True, allow_blank=True)
    media = serializers.CharField(allow_null=True, allow_blank=True)
    encoding = serializers.CharField(allow_null=True, allow_blank=True)

    torrent_name = serializers.CharField(allow_null=True, allow_blank=True)
    torrent_info_hash = serializers.CharField(allow_null=True, allow_blank=True)
    additional_data = serializers.JSONField(allow_null=True)
