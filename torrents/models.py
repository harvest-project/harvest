from django.db import models

from torrents.exceptions import AlcazarNotConfiguredException


class Realm(models.Model):
    """Creates a scope for torrents. Usually it's a 1:1 mapping with trackers, but custom ones can be created."""

    name = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ('name',)


class AlcazarClientConfig(models.Model):
    """Singleton model for storing the information to access alcazard."""

    base_url = models.CharField(max_length=2048)
    token = models.CharField(max_length=64)

    @classmethod
    def get_locked_config(cls):
        try:
            return cls.objects.select_for_update().get()
        except cls.DoesNotExist:
            raise AlcazarNotConfiguredException(
                'Client config is missing. Please configure your account through settings.')

    @classmethod
    def get_config(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            raise AlcazarNotConfiguredException(
                'Client config is missing. Please configure your account through settings.')


class TorrentInfo(models.Model):
    """
    Main table for storing tracker-specific torrent information, as fetched from the remote.

    Optionally accompanied by a more in-depth tracker-specific model linked to this one.
    """

    # Link to the Realm, in which this TorrentInfo belongs
    realm = models.ForeignKey(Realm, models.CASCADE, related_name='torrent_infos')

    # If the original is deleted, instead of deleting it from DB, we can just mark it as is_deleted=True
    is_deleted = models.BooleanField()
    # Info hash of the torrent inside.
    info_hash = models.CharField(max_length=40, db_index=True)
    # Tracker-specific torrent identifier. In most cases this is a torrent_id in some for or another.
    tracker_id = models.CharField(max_length=65536)
    # Date when this information was fetched (or updated).
    fetched_datetime = models.DateTimeField()
    # Tracker plugin specific raw tracker data - raw API response or HTML if scraping.
    raw_response = models.TextField()

    class Meta:
        index_together = (
            ('realm', 'info_hash'),
        )

        unique_together = (
            ('realm', 'tracker_id'),
        )


class TorrentFile(models.Model):
    """Table for storing .torrent files separately from TorrentInfo, in order to keep the table size smaller"""

    # Link to the TorrentInfo
    torrent_info = models.OneToOneField(TorrentInfo, models.CASCADE, related_name='torrent_file')
    # When it was fetched from the tracker
    fetched_datetime = models.DateTimeField()
    # Original filename of the .torrent file, as supplied by the tracker
    torrent_filename = models.CharField(max_length=65536)
    # Binary contents of the .torrent file
    torrent_file = models.BinaryField()


class Torrent(models.Model):
    """Main table for torrents that are present in a torrent client."""

    realm = models.ForeignKey(Realm, models.PROTECT, related_name='torrents')
    torrent_info = models.OneToOneField(TorrentInfo, models.PROTECT, null=True, related_name='torrent')

    info_hash = models.CharField(max_length=40, db_index=True)
    download_path = models.CharField(max_length=65536)
    name = models.TextField(null=True)
    size = models.BigIntegerField(null=True)
    downloaded = models.BigIntegerField(null=True)
    uploaded = models.BigIntegerField(null=True)
    download_rate = models.BigIntegerField(null=True)
    upload_rate = models.BigIntegerField(null=True)
    progress = models.FloatField(null=True)
    added_datetime = models.DateTimeField(null=True)
    error = models.TextField(max_length=65536, null=True, db_index=True)

    class Meta:
        unique_together = ('realm', 'info_hash')


class DownloadLocation(models.Model):
    """Table for download locations - patterns to use to determine where downloads are stored."""

    realm = models.ForeignKey(Realm, models.CASCADE, related_name='download_locations')
    pattern = models.CharField(max_length=65536)

    class Meta:
        unique_together = (('realm', 'pattern'),)
        ordering = ('realm', 'pattern')
