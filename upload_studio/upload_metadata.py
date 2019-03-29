from rest_framework import serializers


class MusicMetadata:
    FORMAT_FLAC = 'FLAC'
    FORMAT_MP3 = 'MP3'
    FORMATS = {
        FORMAT_FLAC,
        FORMAT_MP3,
    }

    MEDIA_CD = 'CD'
    MEDIA_DVD = 'DVD'
    MEDIA_VINYL = 'Vinyl'
    MEDIA_SOUNDBOARD = 'Soundboard'
    MEDIA_SACD = 'SACD'
    MEDIA_DAT = 'DAT'
    MEDIA_CASSETTE = 'Cassette'
    MEDIA_WEB = 'WEB'
    MEDIA_BLU_RAY = 'Blu-Ray'
    MEDIAS = {
        MEDIA_CD,
        MEDIA_DVD,
        MEDIA_VINYL,
        MEDIA_SOUNDBOARD,
        MEDIA_SACD,
        MEDIA_DAT,
        MEDIA_CASSETTE,
        MEDIA_WEB,
        MEDIA_BLU_RAY,
    }

    BITRATE_192 = '192'
    BITRATE_APS = 'APS (VBR)'
    BITRATE_V2 = 'V2 (VBR)'
    BITRATE_V1 = 'V1 (VBR)'
    BITRATE_256 = '256'
    BITRATE_APX = 'APX (VBR)'
    BITRATE_V0 = 'V0 (VBR)'
    BITRATE_320 = '320'
    BITRATE_LOSSLESS = 'Lossless'
    BITRATE_24BIT_LOSSLESS = '24bit Lossless'
    BITRATE_OTHER = 'Other'
    BITRATE = {
        BITRATE_192,
        BITRATE_APS,
        BITRATE_V2,
        BITRATE_V1,
        BITRATE_256,
        BITRATE_APX,
        BITRATE_V0,
        BITRATE_320,
        BITRATE_LOSSLESS,
        BITRATE_24BIT_LOSSLESS,
        BITRATE_OTHER,
    }

    def __init__(self, title=None, edition_year=None, edition_title=None, edition_record_label=None,
                 edition_catalog_number=None, format=None, media=None, bitrate=None, additional_data=None):
        self.title = title
        self.edition_year = edition_year
        self.edition_title = edition_title
        self.edition_record_label = edition_record_label
        self.edition_catalog_number = edition_catalog_number

        self.format = format
        self.media = media
        self.bitrate = bitrate

        self.additional_data = additional_data


class MusicMetadataSerializer(serializers.Serializer):
    title = serializers.CharField()
    edition_year = serializers.IntegerField()
    edition_title = serializers.CharField()
    edition_record_label = serializers.CharField()
    edition_catalog_number = serializers.CharField()

    format = serializers.CharField()
    media = serializers.CharField()
    bitrate = serializers.CharField()

    additional_data = serializers.JSONField()
