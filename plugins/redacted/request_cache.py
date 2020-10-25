import json

from django.db import transaction, IntegrityError
from django.utils import timezone

from plugins.redacted.client import RedactedClient
from plugins.redacted.models import RedactedRequestCacheEntry


class RedactedRequestCache:
    def __init__(self, default_ttl=None):
        self.client = RedactedClient()
        self.default_ttl = default_ttl

    @transaction.atomic
    def _get_cached_or_fetch(self, action, *, ttl=None, **kwargs):
        if ttl is None:
            ttl = self.default_ttl

        kwargs_json = json.dumps(kwargs, sort_keys=True)  # Sort keys for stability of output
        try:
            entry = RedactedRequestCacheEntry.objects.select_for_update().get(
                action=action,
                kwargs_json=kwargs_json,
            )
            if ttl is None or (timezone.now() - entry.fetched_datetime).total_seconds() < ttl:
                return json.loads(entry.response_json)
        except RedactedRequestCacheEntry.DoesNotExist:
            entry = RedactedRequestCacheEntry(
                action=action,
                kwargs_json=kwargs_json,
            )
        response = self.client.request_ajax(action, **kwargs)
        entry.response_json = json.dumps(response)
        entry.fetched_datetime = timezone.now()
        with transaction.atomic():
            try:
                entry.save()
            except IntegrityError:
                pass  # Someone else inserted it in the meantime, nothing to do
        return response

    def get_torrent(self, torrent_id, ttl=None):
        return self._get_cached_or_fetch('torrent', ttl=ttl, id=str(torrent_id))

    def get_torrent_group(self, group_id, ttl=None):
        return self._get_cached_or_fetch('torrentgroup', ttl=ttl, id=str(group_id))

    def get_artist(self, artist_id=None, artist_name=None, ttl=None):
        if artist_id and artist_name:
            raise ValueError('Set exactly one of artist_id or artist_name')
        elif artist_id:
            kwargs = {'id': artist_id}
        elif artist_name:
            kwargs = {'artistname': artist_name}
        else:
            raise ValueError('Set exactly one of artist_id or artist_name')
        return self._get_cached_or_fetch('artist', ttl=ttl, **kwargs)

    def browse(self, search_string, page=1, categories=None, ttl=None):
        categories_kwargs = None
        if categories is not None:
            categories_kwargs = {'filter_cat[{}]'.format(c): '1' for c in categories}
        return self._get_cached_or_fetch(
            'browse',
            ttl=ttl,
            searchstr=search_string,
            page=page,
            **categories_kwargs,
        )
