from rest_framework import serializers

from torrents.models import AlcazarClientConfig, Realm, Torrent, TorrentInfo, DownloadLocation
from trackers.registry import TrackerRegistry


class AlcazarClientConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlcazarClientConfig
        fields = ('base_url', 'token', 'unify_single_file_torrents')


class RealmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Realm
        fields = ('id', 'name')


class TorrentInfoSerializer(serializers.ModelSerializer):
    metadata = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.metadata_serializers_by_realm_id = None

    def _ensure_metadata_serializers_by_realm_id(self):
        if self.metadata_serializers_by_realm_id is not None:
            return

        realms_by_name = {r.name: r for r in Realm.objects.all()}
        self.metadata_serializers_by_realm_id = {}
        for tracker in TrackerRegistry.get_plugins():
            realm = realms_by_name[tracker.name]
            if not realm:
                continue
            serializer_class = tracker.torrent_info_metadata_serializer_class
            if serializer_class is None:
                continue
            serializer = serializer_class()
            serializer.bind('metadata', self)
            self.metadata_serializers_by_realm_id[realm.id] = serializer

    def get_metadata(self, obj):
        if not self.context.get('serialize_metadata', True):
            return None
        self._ensure_metadata_serializers_by_realm_id()
        metadata_serializer = self.metadata_serializers_by_realm_id.get(obj.realm_id)
        if metadata_serializer:
            return metadata_serializer.to_representation(obj)

    class Meta:
        model = TorrentInfo
        fields = ('info_hash', 'tracker_id', 'fetched_datetime', 'metadata')


class TorrentSerializer(serializers.ModelSerializer):
    realm = serializers.IntegerField(source='realm_id')
    torrent_info = TorrentInfoSerializer()

    @classmethod
    def get_context_from_request_data(cls, data):
        return {
            'serialize_metadata': bool(int(data.get('serialize_metadata', '1')))
        }

    class Meta:
        model = Torrent
        fields = '__all__'


class DownloadLocationSerializer(serializers.ModelSerializer):
    realm = serializers.PrimaryKeyRelatedField(queryset=Realm.objects.all())

    class Meta:
        model = DownloadLocation
        fields = '__all__'
