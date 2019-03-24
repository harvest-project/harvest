from rest_framework import serializers

from plugins.bibliotik.models import BibliotikClientConfig, BibliotikTorrent


class BibliotikClientConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = BibliotikClientConfig
        fields = ('username', 'password', 'is_server_side_login_enabled',
                  'login_datetime', 'cookies', 'last_login_failed')
        read_only_fields = ('login_datetime', 'cookies', 'last_login_failed')


class BibliotikTorrentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BibliotikTorrent
        fields = '__all__'


class BibliotikTorrentInfoMetadataSerializer(serializers.Serializer):
    torrent = BibliotikTorrentSerializer(source='bibliotik_torrent')
