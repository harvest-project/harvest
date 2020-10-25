from rest_framework import serializers


class ProjectMetadata:
    def __init__(self, torrent_name, torrent_info_hash, additional_data, processing_steps):
        self.torrent_name = torrent_name
        self.torrent_info_hash = torrent_info_hash
        self.additional_data = additional_data
        self.processing_steps = processing_steps


class ProjectMetadataSerializer(serializers.Serializer):
    torrent_name = serializers.CharField(allow_null=True, allow_blank=True)
    torrent_info_hash = serializers.CharField(allow_null=True, allow_blank=True)
    additional_data = serializers.DictField(allow_null=True)
    processing_steps = serializers.ListField(allow_null=True)


class MusicMetadata(ProjectMetadata):
    # Currently matching the settings in Gazelle
    RELEASE_TYPE_ALBUM = 1
    RELEASE_TYPE_SOUNDTRACK = 3
    RELEASE_TYPE_EP = 5
    RELEASE_TYPE_ANTHOLOGY = 6
    RELEASE_TYPE_COMPLIATION = 7
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

    def __init__(
            self,
            *,
            artist=None,
            title=None,
            original_year=None,
            release_type=None,
            edition_year=None,
            edition_title=None,
            edition_record_label=None,
            edition_catalog_number=None,
            tags=None,
            album_description=None,
            cover_url=None,
            format=None,
            media=None,
            encoding=None,
            torrent_name=None,
            torrent_info_hash=None,
            additional_data=None,
            processing_steps=None,
    ):
        super().__init__(
            torrent_name=torrent_name,
            torrent_info_hash=torrent_info_hash,
            additional_data=additional_data,
            processing_steps=processing_steps or [],
        )

        # TODO: Replace this with a proper list of artists
        self.artist = artist
        self.title = title
        self.original_year = original_year
        self.release_type = release_type
        self.edition_year = edition_year
        self.edition_title = edition_title
        self.edition_record_label = edition_record_label
        self.edition_catalog_number = edition_catalog_number
        self.tags = tags
        self.album_description = album_description
        self.cover_url = cover_url

        self.format = format
        self.media = media
        self.encoding = encoding

    @property
    def format_is_lossy(self):
        return self.format != MusicMetadata.FORMAT_FLAC

    @classmethod
    def get_encoding_from_bit_depth(cls, bit_depth):
        return {
            16: MusicMetadata.ENCODING_LOSSLESS,
            24: MusicMetadata.ENCODING_24BIT_LOSSLESS,
        }[bit_depth]


class MusicMetadataSerializer(ProjectMetadataSerializer):
    artist = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    title = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    original_year = serializers.IntegerField(allow_null=True, required=False)
    release_type = serializers.IntegerField(allow_null=True, required=False)
    edition_year = serializers.IntegerField(allow_null=True, required=False)
    edition_title = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    edition_record_label = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    edition_catalog_number = serializers.CharField(
        allow_null=True, allow_blank=True, required=False)
    tags = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    album_description = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    cover_url = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    format = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    media = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    encoding = serializers.CharField(allow_null=True, allow_blank=True, required=False)
