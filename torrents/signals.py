import django.dispatch

torrent_added = django.dispatch.Signal()
torrent_updated = django.dispatch.Signal()
torrent_removed = django.dispatch.Signal()
