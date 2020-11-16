import base64

import zipstream
from django.db import transaction
from django.db.models import Q
from django.http import StreamingHttpResponse
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from Harvest.utils import TransactionAPIView, CORSBrowserExtensionView, union_dicts
from torrents.add_torrent import add_torrent_from_file, add_torrent_from_tracker, fetch_torrent
from torrents.alcazar_client import AlcazarClient, AlcazarRemoteException
from torrents.exceptions import RealmNotFoundException
from torrents.models import AlcazarClientConfig, Realm, Torrent, DownloadLocation
from torrents.remove_torrent import remove_torrent
from torrents.serializers import AlcazarClientConfigSerializer, RealmSerializer, TorrentSerializer, \
    DownloadLocationSerializer, TorrentInfoSerializer
from torrents.utils import get_zip_download_filename_base, add_zip_download_files
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
        client = AlcazarClient(timeout=AlcazarClient.TIMEOUT_LONG)
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

    TORRENT_SELECT_RELATED = ('torrent_info',) + sum(
        (t.torrents_select_related for t in TrackerRegistry.get_plugins()), ())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            return qs.order_by('-added_datetime')
        return qs.order_by(order_by)

    def get_serializer_context(self):
        params = union_dicts(self.request.query_params, self.request.data)
        return TorrentSerializer.get_context_from_request_data(params)

    def get_queryset(self):
        torrents = Torrent.objects.select_related(*self.TORRENT_SELECT_RELATED)
        params = union_dicts(self.request.query_params, self.request.data)
        torrents = self._apply_status(torrents, params.get('status'))
        torrents = self._apply_realm(torrents, params.get('realm_id'), params.get('realm_name'))
        torrents = self._apply_tracker_ids(torrents, params.get('tracker_ids'))
        torrents = self._apply_order_by(torrents, params.get('order_by'))
        return torrents

    # Workaround to support both GET and POST requests in case filters are expected to be large
    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TorrentView(RetrieveDestroyAPIView):
    serializer_class = TorrentSerializer

    def get_serializer_context(self):
        return TorrentSerializer.get_context_from_request_data(self.request.query_params)

    def get_object(self):
        raise NotImplementedError()

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        torrent = self.get_object()
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
    def get_object(self):
        try:
            return Torrent.objects.get(id=self.kwargs['torrent_id'])
        except Torrent.DoesNotExist:
            raise NotFound()


class TorrentZip(TorrentByIDView):
    def get(self, request, torrent_id):
        torrent = self.get_object()
        zip_file = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_STORED, allowZip64=True)
        filename_base = get_zip_download_filename_base(torrent)
        add_zip_download_files(zip_file, torrent)
        response = StreamingHttpResponse(zip_file, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}'.format(f'{filename_base}.zip')
        return response


class TorrentByRealmInfoHash(TorrentView, APIView):
    def get_object(self):
        try:
            realm = Realm.get_by_name_or_id(self.kwargs['realm'])
        except Realm.DoesNotExist:
            raise NotFound()
        try:
            return Torrent.objects.get(realm=realm, info_hash=self.kwargs['info_hash'])
        except Torrent.DoesNotExist:
            raise NotFound()


class TorrentByRealmTrackerId(TorrentView, APIView):
    def get_object(self):
        try:
            realm = Realm.get_by_name_or_id(self.kwargs['realm'])
        except Realm.DoesNotExist:
            raise NotFound()
        try:
            return Torrent.objects.get(
                realm=realm,
                torrent_info__tracker_id=self.kwargs['tracker_id'],
            )
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
        download_path_pattern = request.data.get('download_path')

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
        download_path_pattern = request.data.get('download_path')

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
