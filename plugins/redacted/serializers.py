from rest_framework import serializers

from plugins.redacted.models import RedactedClientConfig


class RedactedClientConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedactedClientConfig
        fields = ('username', 'password', 'login_datetime', 'cookies', 'last_login_failed')
        read_only_fields = ('login_datetime', 'cookies', 'last_login_failed')
