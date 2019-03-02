from django.urls import path

from . import views

urlpatterns = [
    path('by-id/<torrent_id>', views.TorrentByIDView.as_view()),
    path('realms', views.Realms.as_view()),
    path('realms/<realm_name>/torrents/<info_hash>', views.TorrentByRealmInfoHash.as_view()),
    path('alcazar-client/config', views.AlcazarClientConfigView.as_view()),
    path('alcazar-client/connection-test', views.AlcazarConnectionTest.as_view()),
    path('alcazar/config', views.AlcazarConfigView.as_view()),
    path('alcazar/clients', views.AlcazarClients.as_view()),
    path('', views.Torrents.as_view()),
    path('add-torrent-from-file', views.AddTorrentFromFile.as_view()),
]
