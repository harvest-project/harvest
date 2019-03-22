import json

from rest_framework import serializers

from plugins.redacted.models import RedactedClientConfig, RedactedTorrent, RedactedTorrentGroup
from plugins.redacted.utils import get_joined_artists


class RedactedClientConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedactedClientConfig
        fields = ('username', 'password', 'login_datetime', 'cookies', 'last_login_failed')
        read_only_fields = ('login_datetime', 'cookies', 'last_login_failed')


class RedactedTorrentGroupSerializer(serializers.ModelSerializer):
    joined_artists = serializers.SerializerMethodField()

    def get_joined_artists(self, obj):
        return get_joined_artists(json.loads(obj.music_info))

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
