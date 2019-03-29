from rest_framework import serializers

from monitoring.models import LogEntry, ComponentStatus


class ComponentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentStatus
        fields = '__all__'


class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = '__all__'
