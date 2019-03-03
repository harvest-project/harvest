from rest_framework import serializers


class DownloadLocationComponentSerializer(serializers.Serializer):
    key = serializers.CharField()
    description = serializers.CharField()
    example = serializers.CharField()


class TrackerSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    download_location_components = DownloadLocationComponentSerializer(many=True)
