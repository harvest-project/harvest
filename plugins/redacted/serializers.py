from rest_framework import serializers

from plugins.redacted.models import RedactedClientConfig, RedactedTorrent, RedactedTorrentGroup


class RedactedClientConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedactedClientConfig
        fields = ('api_key', 'announce_url', 'last_login_failed')
        read_only_fields = ('last_login_failed',)


class RedactedTorrentGroupSerializer(serializers.ModelSerializer):
    joined_artists = serializers.CharField()

    class Meta:
        model = RedactedTorrentGroup
        fields = '__all__'


class RedactedTorrentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedactedTorrent
        fields = '__all__'


class RedactedTorrentInfoMetadataSerializer(serializers.Serializer):
    group = RedactedTorrentGroupSerializer(source='redacted_torrent.torrent_group')
    torrent = RedactedTorrentSerializer(source='redacted_torrent')
