import pickle
from http import cookiejar

from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from Harvest.cookie_utils import cookie_to_dict, cookie_from_dict
from Harvest.utils import TransactionAPIView, CORSBrowserExtensionView, get_logger
from plugins.bibliotik.client import BibliotikClient
from plugins.bibliotik.models import BibliotikClientConfig
from plugins.bibliotik.serializers import BibliotikClientConfigSerializer

logger = get_logger(__name__)


class Config(TransactionAPIView, RetrieveUpdateDestroyAPIView):
    """Configure the Bibliotik integration plugin."""

    serializer_class = BibliotikClientConfigSerializer

    def get_object(self):
        try:
            return BibliotikClientConfig.objects.select_for_update().get()
        except BibliotikClientConfig.DoesNotExist:
            return BibliotikClientConfig(
                is_server_side_login_enabled=True,
            )

    # After a username/password update, set last_login_failed to False
    def perform_update(self, serializer):
        serializer.instance.last_login_failed = False
        serializer.instance.clear_login_data()
        super().perform_update(serializer)


class ConnectionTest(APIView):
    """Test the connection of the plugin to the user's Bibliotik account."""

    def post(self, request):
        try:
            client = BibliotikClient()
            client.get_index()
            return Response({'success': True})
        except Exception as ex:
            return Response({'success': False, 'detail': str(ex)})


class ClearLoginData(TransactionAPIView, APIView):
    def post(self, request):
        config = BibliotikClientConfig.objects.select_for_update().get()
        config.last_login_failed = False
        config.clear_login_data()
        config.save()
        return Response({'success': True})


class Cookies(CORSBrowserExtensionView, APIView):
    def _get_response_from_config(self, config):
        if config and config.cookies:
            return Response({
                'cookies': [cookie_to_dict(c) for c in pickle.loads(config.cookies)],
            })
        return Response({'cookies': []})

    def get(self, request):
        config = BibliotikClientConfig.objects.first()
        return self._get_response_from_config(config)

    def put(self, request):
        input_jar = cookiejar.CookieJar()
        for cookie_data in request.data['cookies']:
            input_jar.set_cookie(cookie_from_dict(cookie_data))

        client = BibliotikClient()

        # Try to reconcile offered vs. stored cookies.
        config = client.accept_cookies_if_ok(input_jar)

        # If we're left without cookies, try to login server-side, if enabled
        if not config.cookies and config.is_server_side_login_enabled:
            logger.debug('No working cookies found, trying server-side login.')
            try:
                client.get_index()
                config.refresh_from_db()
                logger.debug('Server-side login is working.')
            except:
                # Swallow exceptions, so we don't fail the client if we can't login.
                logger.debug('Server-side login is also not working.')

        return self._get_response_from_config(config)
