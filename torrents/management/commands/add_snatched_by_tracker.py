from bencode import bdecode
import os
import shutil

from django.core.management import BaseCommand

from torrents.download_locations import format_download_path_pattern
from torrents.models import TorrentInfo, TorrentFile, Realm, Torrent
from torrents.add_torrent import add_torrent_from_tracker, fetch_torrent
from torrents.exceptions import RealmNotFoundException

from trackers.registry import TrackerRegistry

from plugins.redacted.client import RedactedClient

# TODO
# Make the command able to add torrents for non-plugin trackers


class TorrentMover:
    """Moves or copies torrent contents"""


    def __init__(self, to_copy=True, base_dir='', torrent_file=None, torrent_info=None):
        """
        Initializes TorrentMover

        Args:
            base_dir (str): Where to look for the torrent contents
            to_copy (bool): True if you want to copy files, False if you want to move them
            torrent_info (TorrentInfo)
            torrent_file (TorrentFile)

        Notes:
            - base_dir should almost always be defined
            - only one of torrent_info or torrent_file needs to be defined
            - torrent_info has priority over torrent_file if both defined
            - If using store_files_hook, neither needs to be defined
        """
        self.to_copy = to_copy
        self.base_dir = base_dir
        self.torrent_file_decoded = None
        self.file_list = None

        torrent_bytes = None
        if torrent_file is not None:
            torrent_bytes = bytes(torrent_file.torrent_file)
        if torrent_info is not None:
            torrent_bytes = bytes(torrent_info.torrent_file.torrent_file)
        if torrent_bytes is not None:
            self.torrent_file_decoded = bdecode(torrent_bytes)
        

    def _set_file_list(self):
        # file_list is relative to the parent directory of the torrent contents
        file_list = []
        torrent_info = self.torrent_file_decoded.get('info')
        if 'files' in torrent_info:
            # folder case
            folder = torrent_info['name']
            
            for individual_file in torrent_info['files']:
                # joins full path of each file
                individual_path = ''
                for path_part in individual_file['path']:
                    individual_path = os.path.join(individual_path, path_part)

                file_list.append(os.path.join(folder, individual_path))            
        else:
            # single file case
            file_list.append(torrent_info['name'])
        self.file_list = file_list

    def contains_files(self):
        """
        Checks if all the torrent contents are in base_dir

        returns: bool
        """
        if self.file_list is None:
            self._set_file_list()
        for individual_file in self.file_list:
            if not os.path.exists(os.path.join(self.base_dir, individual_file)):
                return False
        return True

    def move_files(self, download_path):
        """
        Moves all of this torrent's contents to a new location

        Args:
        download_path: Where to copy the contents of this torrent to

        Returns: None
        """
        if self.file_list is None:
            self._set_file_list()
        
        for individual_file in self.file_list:
            source_path = os.path.join(self.base_dir, individual_file)
            dest_path = os.path.join(download_path, individual_file)
            print(individual_file)
            # We don't move files that don't exist
            if not os.path.exists(source_path):
                continue
            
            # Make sure the destination directory exists
            if not os.path.exists(os.path.dirname(dest_path)):
                os.makedirs(os.path.dirname(dest_path))
            if self.to_copy:
                shutil.copy(source_path, dest_path)
            else:
                os.rename(source_path, dest_path)
        return
    
    def store_files_hook(self, torrent_info, download_path):
        """
        Moves all of this torrent's contents to a new location

        Note:
            torrent_info takes precedence over existing torrent_file or torrent_info
        
        Args:
            torrent_info (TorrentInfo)
            download_path (str): Where to copy the contents of this torrent to

        Returns: None
        """
        torrent_bytes = bytes(torrent_info.torrent_file.torrent_file)
        self.torrent_file_decoded = bdecode(torrent_bytes)
        self.move_files(download_path)




class Command(BaseCommand):
    help="""Adds torrents that you have snatched, but are not currently seeding"""

    def handle_single_torrent(self, realm, tracker, tracker_id, reject_missing, 
                            source_path_pattern, download_path_pattern, to_copy=True):
        torrent_info = fetch_torrent(realm, tracker, tracker_id, force_fetch=False)
        torrent_file_bytes = bytes(torrent_info.torrent_file.torrent_file)
        base_dir = format_download_path_pattern(source_path_pattern, 
                    torrent_file_bytes, torrent_info)
        
        tm = TorrentMover(base_dir=base_dir, to_copy=to_copy, torrent_info=torrent_info)
        
        if not tm.contains_files():
            if reject_missing:
                return
        
        file_hook = tm.store_files_hook
        added_torrent = add_torrent_from_tracker(
            tracker=tracker,
            tracker_id=tracker_id,
            download_path_pattern=download_path_pattern,
            force_fetch=True,
            store_files_hook=file_hook
        )

    def add_missing_from_tracker(self,*, tracker, download_path_pattern=None, 
                            source_path_pattern=None, reject_missing=True, to_copy=True):
    
        try:
            realm = Realm.objects.get(name=tracker.name)
        except Realm.DoesNotExist:
            raise RealmNotFoundException(tracker.name)

        # RED hardcoded in currently
        # checks if tracker client supports getting snatch history
        # if getattr(tracker, 'get_snatched', None) is None:
        #     print('Tracker plugin does not support get_snatched')
        #     return
     
        active_tracker_ids = set()
        active_torrents = Torrent.objects.filter(realm=realm)
        for torrent in active_torrents:
            active_tracker_ids.add(int(torrent.torrent_info.tracker_id))

        offset = 0
        limit = 500
        
        # This API does not exist
        # snatched_list = tracker.get_snatched(offset, limit)
        red_client = RedactedClient()
        snatched_list = red_client.get_snatched(offset, limit)['snatched']
        while len(snatched_list) != 0:
            for torrent in snatched_list:
                #Make sure it isn't already seeding
                tracker_id = torrent['torrentId']
                if tracker_id in active_tracker_ids:
                    continue
                active_tracker_ids.add(tracker_id)

                self.handle_single_torrent(realm, tracker, tracker_id, reject_missing, 
                            source_path_pattern, download_path_pattern, to_copy=to_copy)
            offset += limit
            snatched_list = red_client.get_snatched(offset, limit)['snatched']
    

    def add_arguments(self, parser):
        parser.add_argument(
            '--tracker',
            help='Name of tracker, example: redacted',
            type=str,
            required=True
        )        
        parser.add_argument(
            '--source-path-pattern',
            type=str, 
            help='Where to look for torrent contents',
            required=True
        )
        parser.add_argument(
            '--download-path-pattern',
            type=str, 
            help='Where to seed torrent contents from',
            required=True
        )
        parser.add_argument('--add-missing', 
            action='store_true', 
            help='Adds torrents that cannot be found in source_path_pattern',
            default=False
        )
        parser.add_argument(
            '--copy',
            help='Copies files instead of moving them in', 
            action='store_true',
            default=False
        )


    def handle(self, *args, **options):
        if options['tracker'] != 'redacted':
            print('Only redacted support so far')
            return 
        # TODO Probably should do some validation here
        self.add_missing_from_tracker(
            tracker=TrackerRegistry.get_plugin(options['tracker'], self.__class__.__name__),
            source_path_pattern=options['source_path_pattern'],
            download_path_pattern=options['download_path_pattern'],
            reject_missing=not options['add_missing'],
            to_copy=options['copy']
        )
   