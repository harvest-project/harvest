from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.CharField()
    is_superuser = serializers.BooleanField()
    full_name = serializers.CharField(source='get_full_name', read_only=True)
