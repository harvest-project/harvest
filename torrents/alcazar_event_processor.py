import logging
import time
from collections import defaultdict

from torrents.alcazar_client import update_torrent_from_alcazar, \
    create_or_update_torrent_from_alcazar
from torrents.models import Torrent, Realm, TorrentInfo
from torrents.signals import torrent_removed

logger = logging.getLogger(__name__)


class AlcazarEventProcessor:
    @classmethod
    def _process_removed_events(cls, removed_info_hashes):
        removed_torrents_qs = Torrent.objects.filter(info_hash__in=removed_info_hashes)
        removed_info_hashes = list(removed_torrents_qs.values_list('info_hash', flat=True))
        logger.debug('Matched {} Torrent objects for deletion.'.format(len(removed_info_hashes)))
        removed_torrents_qs.delete()
        for removed_info_hash in removed_info_hashes:
            torrent_removed.send(removed_info_hash)

    @classmethod
    def _process_added_torrents(cls, realm, added_torrent_states):
        realms = {realm.name: realm for realm in Realm.objects.all()}
        info_hashes = [state['info_hash'] for state in added_torrent_states]
        torrent_info_ids = {
            item[0]: item[1] for item in
            TorrentInfo.objects.filter(realm=realm, info_hash__in=info_hashes).values_list('info_hash', 'id')}

        for added_state in added_torrent_states:
            realm = realms.get(added_state['realm'])
            if not realm:
                realm, _ = Realm.objects.get_or_create(name=added_state['realm'])

            create_or_update_torrent_from_alcazar(
                realm=realm,
                torrent_info_id=torrent_info_ids.get(added_state['info_hash']),
                torrent_state=added_state,
            )

    @classmethod
    def _process_events(cls, realm, events):
        cls._process_removed_events(events['removed'])

        updated_info_hashes = [state['info_hash'] for state in events['updated']]
        existing_torrents = {
            t.info_hash: t for t in Torrent.objects.filter(realm=realm, info_hash__in=updated_info_hashes)}
        added_torrents_states = []

        logger.debug('Matched {} Torrent objects for updating.'.format(len(existing_torrents)))

        num_updated = 0
        for updated_state in events['updated']:
            torrent = existing_torrents.get(updated_state['info_hash'])
            if not torrent:
                added_torrents_states.append(updated_state)
            else:
                if update_torrent_from_alcazar(torrent, updated_state):
                    num_updated += 1

        logger.debug('Actually updated {} in DB.'.format(num_updated))
        logger.debug('Matched {} new states for adding.'.format(len(added_torrents_states)))

        cls._process_added_torrents(realm, added_torrents_states)

    @classmethod
    def process(cls, events):
        start = time.time()
        updates_per_realm = defaultdict(lambda: {'removed': [], 'updated': []})

        logger.debug('Splitting events in realms.')

        for removed_realm, removed_info_hash in events['removed']:
            updates_per_realm[removed_realm]['removed'].append(removed_info_hash)

        for updated_state in events['updated']:
            updates_per_realm[updated_state['realm']]['updated'].append(updated_state)

        logger.debug('Processing events.')

        realms = {realm.name: realm for realm in Realm.objects.all()}
        for realm_name, updates in updates_per_realm.items():
            realm = realms.get(realm_name)
            if not realm:
                realm, _ = Realm.objects.get_or_create(name=realm_name)

            logger.debug('Processing events for realm {}.'.format(realm_name))
            cls._process_events(realm, updates)

        logger.debug('Completed alcazar update in {}.'.format(time.time() - start))
