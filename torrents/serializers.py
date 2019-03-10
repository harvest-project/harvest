from rest_framework import serializers

from torrents.models import AlcazarClientConfig, Realm, Torrent, TorrentInfo, DownloadLocation


class AlcazarClientConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlcazarClientConfig
        fields = ('base_url', 'token')


class RealmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Realm
        fields = ('id', 'name')


class TorrentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TorrentInfo
        fields = ('info_hash', 'tracker_id', 'fetched_datetime')


class TorrentSerializer(serializers.ModelSerializer):
    realm = serializers.PrimaryKeyRelatedField(queryset=Realm.objects.all())
    torrent_info = TorrentInfoSerializer()

    class Meta:
        model = Torrent
        fields = ('id', 'realm', 'torrent_info', 'info_hash', 'status', 'download_path', 'name', 'size', 'downloaded',
                  'uploaded', 'download_rate', 'upload_rate', 'progress', 'added_datetime', 'error', 'tracker_error',
                  'client')


class DownloadLocationSerializer(serializers.ModelSerializer):
    realm = serializers.PrimaryKeyRelatedField(queryset=Realm.objects.all())

    class Meta:
        model = DownloadLocation
        fields = ('id', 'realm', 'pattern')
        depth = 1
