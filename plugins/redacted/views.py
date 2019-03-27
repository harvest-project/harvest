from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from Harvest.utils import TransactionAPIView
from plugins.redacted.client import RedactedClient
from plugins.redacted.models import RedactedClientConfig
from plugins.redacted.serializers import RedactedClientConfigSerializer


class Config(TransactionAPIView, RetrieveUpdateDestroyAPIView):
    serializer_class = RedactedClientConfigSerializer

    def get_object(self):
        try:
            return RedactedClientConfig.objects.select_for_update().get()
        except RedactedClientConfig.DoesNotExist:
            return RedactedClientConfig()

    # After a username/password update, set last_login_failed to False
    def perform_update(self, serializer):
        serializer.instance.last_login_failed = False
        serializer.instance.clear_login_data()
        super().perform_update(serializer)


class ConnectionTest(APIView):
    def post(self, request):
        try:
            client = RedactedClient()
            client.get_index()
            return Response({'success': True})
        except Exception as ex:
            return Response({'success': False, 'detail': str(ex)})


class ClearLoginData(TransactionAPIView, APIView):
    def post(self, request):
        config = RedactedClientConfig.objects.select_for_update().get()
        config.last_login_failed = False
        config.clear_login_data()
        config.save()
        return Response({'success': True})
