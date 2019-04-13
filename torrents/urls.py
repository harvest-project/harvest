from django.urls import path

from . import views

urlpatterns = [
    path('', views.Torrents.as_view()),
    path('by-id/<torrent_id>', views.TorrentByID.as_view()),
    path('by-id/<torrent_id>/zip', views.TorrentZip.as_view()),
    path('realms', views.Realms.as_view()),
    path('realms/<realm>/by-info-hash/<info_hash>', views.TorrentByRealmInfoHash.as_view()),
    path('realms/<realm>/by-tracker-id/<tracker_id>', views.TorrentByRealmTrackerId.as_view()),
    path('alcazar-client/config', views.AlcazarClientConfigView.as_view()),
    path('alcazar-client/connection-test', views.AlcazarConnectionTest.as_view()),
    path('alcazar/config', views.AlcazarConfigView.as_view()),
    path('alcazar/clients', views.AlcazarClients.as_view()),
    path('fetch-torrent', views.FetchTorrent.as_view()),
    path('add-torrent-from-file', views.AddTorrentFromFile.as_view()),
    path('add-torrent-from-tracker', views.AddTorrentFromTracker.as_view()),
    path('download-locations', views.DownloadLocations.as_view()),
    path('download-locations/<pk>', views.DownloadLocationView.as_view()),
]
