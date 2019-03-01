from rest_framework import serializers

from plugins.bibliotik.models import BibliotikClientConfig


class BibliotikClientConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = BibliotikClientConfig
        fields = ('username', 'password', 'is_server_side_login_enabled',
                  'login_datetime', 'cookies', 'last_login_failed')
        read_only_fields = ('login_datetime', 'cookies', 'last_login_failed')
