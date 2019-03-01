from rest_framework import serializers


class TrackerSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)
