import base64

from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from Harvest.utils import TransactionAPIView, CORSBrowserExtensionView
from torrents.add_torrent import add_torrent_from_file, add_torrent_from_tracker, fetch_torrent
from torrents.alcazar_client import AlcazarClient, AlcazarRemoteException
from torrents.exceptions import RealmNotFoundException
from torrents.models import AlcazarClientConfig, Realm, Torrent, DownloadLocation
from torrents.remove_torrent import remove_torrent
from torrents.serializers import AlcazarClientConfigSerializer, RealmSerializer, TorrentSerializer, \
    DownloadLocationSerializer, TorrentInfoSerializer
from trackers.registry import TrackerRegistry


class Realms(ListAPIView):
    queryset = Realm.objects.all()
    serializer_class = RealmSerializer


class AlcazarClientConfigView(TransactionAPIView, RetrieveUpdateDestroyAPIView):
    serializer_class = AlcazarClientConfigSerializer

    def get_object(self):
        try:
            return AlcazarClientConfig.objects.select_for_update().get()
        except AlcazarClientConfig.DoesNotExist:
            return AlcazarClientConfig(
                base_url='http://localhost:7001/',
            )


class AlcazarConnectionTest(APIView):
    def post(self, request):
        try:
            client = AlcazarClient()
            client.ping()
            return Response({'success': True})
        except Exception as ex:
            return Response({'success': False, 'detail': str(ex)})


class AlcazarConfigView(APIView):
    def get(self, request):
        client = AlcazarClient()
        return Response(client.get_config())

    def put(self, request):
        client = AlcazarClient()
        client.save_config(request.data)
        return Response({})


class AlcazarClients(APIView):
    def get(self, request):
        client = AlcazarClient()
        return Response(client.get_clients())

    @transaction.atomic
    def post(self, request):
        Realm.objects.get_or_create(name=request.data['realm'])
        client = AlcazarClient()
        return Response(client.add_client(request.data))


class TorrentsPagination(PageNumberPagination):
    page_size = 100

    def get_page_size(self, request):
        return request.query_params.get('page_size', request.data.get('page_size', self.page_size))


class Torrents(CORSBrowserExtensionView, ListAPIView):
    pagination_class = TorrentsPagination
    serializer_class = TorrentSerializer

    FILTER_ALL = 'all'
    FILTER_ACTIVE = 'active'
    FILTER_DOWNLOADING = 'downloading'
    FILTER_SEEDING = 'seeding'
    FILTER_ERRORS = 'errors'

    FILTER_FUNCS = {
        None: lambda qs: qs,
        FILTER_ALL: lambda qs: qs,
        FILTER_ACTIVE: lambda qs: qs.filter(Q(download_rate__gt=0) | Q(upload_rate__gt=0)),
        FILTER_DOWNLOADING: lambda qs: qs.filter(status=Torrent.STATUS_DOWNLOADING),
        FILTER_SEEDING: lambda qs: qs.filter(status=Torrent.STATUS_SEEDING),
        FILTER_ERRORS: lambda qs: qs.filter(Q(error__isnull=False) | Q(tracker_error__isnull=False)),
    }

    def _get_param(self, name, default=None):
        if name in self.request.query_params:
            return self.request.query_params[name]
        if name in self.request.data:
            return self.request.data[name]
        return default

    def _apply_status(self, qs, status):
        return self.FILTER_FUNCS[status](qs)

    def _apply_realm(self, qs, realm_id, realm_name):
        if realm_name:
            realm_id = Realm.objects.get(name=realm_name).id
        if realm_id:
            return qs.filter(realm_id=int(realm_id))
        return qs

    def _apply_tracker_ids(self, qs, tracker_ids):
        if isinstance(tracker_ids, str):
            tracker_ids = tracker_ids.split(',')
        if tracker_ids:
            return qs.filter(torrent_info__tracker_id__in=tracker_ids)
        return qs

    def _apply_order_by(self, qs, order_by):
        if not order_by:
            return qs
        return qs.order_by(order_by)

    def get_serializer_context(self):
        return {
            'serialize_metadata': bool(int(self._get_param('serialize_metadata', '1'))),
        }

    def get_queryset(self):
        torrents = Torrent.objects.select_related(
            'realm',
            'torrent_info',
        ).order_by('-added_datetime')
        torrents = self._apply_status(torrents, self._get_param('status'))
        torrents = self._apply_realm(torrents, self._get_param('realm_id'), self._get_param('realm_name'))
        torrents = self._apply_tracker_ids(torrents, self._get_param('tracker_ids'))
        torrents = self._apply_order_by(torrents, self._get_param('order_by'))
        return torrents

    # Workaround to support both GET and POST requests in case filters are expected to be large
    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TorrentView(APIView):
    def get_object(self, *args, **kwargs):
        raise NotImplementedError()

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        torrent = self.get_object(*args, **kwargs)
        torrent.delete()
        try:
            remove_torrent(torrent=torrent)
        except AlcazarRemoteException as exc:
            if exc.status_code == 404:
                return Response({
                    'detail': 'Torrent not present in Alcazar. It was deleted from the DB, but please check whether '
                              'sync is running properly.',
                }, status=404)
            raise
        return Response({})


class TorrentByIDView(TorrentView, APIView):
    def get_object(self, torrent_id):
        try:
            return Torrent.objects.get(id=torrent_id)
        except Torrent.DoesNotExist:
            raise NotFound()


class TorrentByRealmInfoHash(TorrentView, APIView):
    def get_object(self, realm_name, info_hash):
        try:
            realm = Realm.objects.get(name=realm_name)
        except Realm.DoesNotExist:
            raise NotFound()
        try:
            return Torrent.objects.get(realm=realm, info_hash=info_hash)
        except Torrent.DoesNotExist:
            raise NotFound()


class FetchTorrent(APIView):
    def post(self, request):
        tracker_name = request.data['tracker_name']
        tracker_id = request.data['tracker_id']
        tracker = TrackerRegistry.get_plugin(tracker_name, self.__class__.__name__)

        try:
            realm = Realm.objects.get(name=tracker.name)
        except Realm.DoesNotExist:
            raise RealmNotFoundException(tracker.name)
        added_torrent = fetch_torrent(realm, tracker, tracker_id)
        return Response(TorrentInfoSerializer(added_torrent).data)


class AddTorrentFromFile(APIView):
    @transaction.atomic
    def post(self, request):
        realm_name = request.data['realm_name']
        torrent_file = base64.b64decode(request.data['torrent_file'])
        download_path_pattern = request.data['download_path']

        try:
            realm = Realm.objects.get(name=realm_name)
        except Realm.DoesNotExist:
            raise RealmNotFoundException(realm_name)
        added_torrent = add_torrent_from_file(
            realm=realm,
            torrent_file=torrent_file,
            download_path_pattern=download_path_pattern,
        )
        return Response(TorrentSerializer(added_torrent).data)


class AddTorrentFromTracker(CORSBrowserExtensionView, APIView):
    def post(self, request):
        tracker_name = request.data['tracker_name']
        tracker_id = request.data['tracker_id']
        download_path_pattern = request.data['download_path']

        tracker = TrackerRegistry.get_plugin(tracker_name, self.__class__.__name__)
        added_torrent = add_torrent_from_tracker(
            tracker=tracker,
            tracker_id=tracker_id,
            download_path_pattern=download_path_pattern,
            force_fetch=True,
        )
        return Response(TorrentSerializer(added_torrent).data)


class DownloadLocations(ListCreateAPIView):
    queryset = DownloadLocation.objects.all().order_by('pattern')
    serializer_class = DownloadLocationSerializer

    def create(self, request, *args, **kwargs):
        if not DownloadLocation.objects.filter(realm_id=request.data['realm'], is_preferred=True).exists():
            request.data['is_preferred'] = True
        return super().create(request, *args, **kwargs)


class DownloadLocationView(RetrieveUpdateDestroyAPIView):
    queryset = DownloadLocation.objects.all()
    serializer_class = DownloadLocationSerializer

    def perform_update(self, serializer):
        super().perform_update(serializer)
        obj = serializer.instance
        if obj.is_preferred:
            DownloadLocation.objects.filter(realm_id=obj.realm_id).exclude(id=obj.id).update(is_preferred=False)
