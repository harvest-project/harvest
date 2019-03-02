import base64

from django.db import transaction
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from Harvest.utils import TransactionAPIView
from torrents.add_torrent import add_torrent_from_file
from torrents.alcazar_client import AlcazarClient, AlcazarRemoteException
from torrents.models import AlcazarClientConfig, Realm, Torrent
from torrents.remove_torrent import remove_torrent
from torrents.serializers import AlcazarClientConfigSerializer, RealmSerializer, TorrentSerializer


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


class Torrents(APIView):
    def get(self, request):
        torrents = Torrent.objects.select_related('realm', 'torrent_info').all()
        return Response({
            'torrents': TorrentSerializer(torrents, many=True).data,
        })


class TorrentView(APIView):
    def get_object(self, *args, **kwargs):
        raise NotImplementedError()

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        torrent = self.get_object(*args, **kwargs)
        torrent.delete()
        try:
            remove_torrent(torrent)
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


class AddTorrentFromFile(APIView):
    @transaction.atomic
    def post(self, request):
        realm = Realm.objects.get(name=request.data['realm'])
        torrent_file = base64.b64decode(request.data['torrent_file'])
        download_path = request.data['download_path']
        added_torrent = add_torrent_from_file(realm, torrent_file, download_path)
        return Response(TorrentSerializer(added_torrent).data)
