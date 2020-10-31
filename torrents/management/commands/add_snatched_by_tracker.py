from bencode import bdecode
import os
import shutil

from django.core.management import BaseCommand

from torrents.download_locations import format_download_path_pattern
from torrents.models import TorrentInfo, TorrentFile, Realm, Torrent
from torrents.add_torrent import add_torrent_from_tracker, fetch_torrent
from torrents.exceptions import RealmNotFoundException

from trackers.registry import TrackerRegistry

class ImportedTorrentMover():
    # store_files_hook for add_missing_from_tracker

    # base_dir:   Location where it looks /mnt/media/music
    # folder:     Name of the folder
    # sub_dir:    All torrent files relative to the folder
    def __init__(self, base_dir=None, sub_dir=None, folder=None, to_copy=True):
        self.base_dir = base_dir
        self.sub_dir = sub_dir
        self.folder = folder
        self.to_copy = to_copy
    
    # Moves all torrent contents to new download_path
    def move_files(self, torrent_info, download_path):
        source_base_dir = self.base_dir
        dest_base_dir = download_path

        if self.folder:
            source_base_dir = os.path.join(source_base_dir,self.folder)
            dest_base_dir = os.path.join(dest_base_dir, self.folder)
        for path in self.sub_dir:
            source_path = os.path.join(source_base_dir, path)
            dest_path = os.path.join(dest_base_dir, path)
            if not os.path.exists(os.path.dirname(dest_path)):
                os.makedirs(os.path.dirname(dest_path))
            if self.to_copy:
                shutil.copy(source_path, dest_path)
            else:
                os.rename(source_path, dest_path)
        return


class Command(BaseCommand):
    def add_missing_from_tracker(self,*, tracker, download_path_pattern=None, 
                            source_path_pattern=None, reject_missing=True, to_copy=True):
    
        try:
            realm = Realm.objects.get(name=tracker.name)
        except Realm.DoesNotExist:
            raise RealmNotFoundException(tracker.name)

        reject_missing = reject_missing
        snatched = None
        offset = 0
        limit = 500
        
        # checks if tracker client supports snatch history
        if getattr(tracker, 'get_snatched', None) == None:
            return
        
        snatched = tracker.get_snatched(offset, limit)
        active_tracker_ids = set()
        active_torrents = Torrent.objects.filter(realm=realm)
        for torrent in active_torrents:
            active_tracker_ids.add(int(torrent.torrent_info.tracker_id))

        while len(snatched) != 0:
            for torrent in snatched:

                tracker_id = torrent['torrentId']
                missing_data = True

                #Make sure it isn't already seeding
                if tracker_id in active_tracker_ids:
                    continue
                
                torrent_info = fetch_torrent(realm, tracker, tracker_id, force_fetch=False)
                torrent_file_bytes = bytes(torrent_info.torrent_file.torrent_file)
                source_path = format_download_path_pattern(source_path_pattern, 
                            torrent_file_bytes, torrent_info)
                decoded = bdecode(torrent_file_bytes).get('info')
                directory_name = decoded.get('name')
                file_list = decoded.get('files')
                file_paths = []
                base_dir = os.path.join(source_path, directory_name)
                #verify data exists at source_pattern
                if file_list == None:
                    # Single file case
                    if os.path.exists(base_dir):
                        missing_data = False
                else:
                    # Folder case
                    for individual_file in file_list:
                        file_path = ""
                        
                        # os.join all parts
                        for each in individual_file['path']:
                            # Bencode returns data in bytes if it is unicode
                            # Decode it here
                            if type(each) == bytes:
                                each = each.decode('unicode_escape')
                            file_path = os.path.join(file_path, each)

                        
                        
                        individual_file_path = os.path.join(base_dir, file_path)
                        if os.path.exists(individual_file_path):
                            file_paths.append(file_path)
                        
                    if len(file_list) == len(file_paths):
                        missing_data = False
                if reject_missing and missing_data:
                    continue

                # Moves file to download_path, and adds torrent
                itm = ImportedTorrentMover(source_path,file_paths, folder=directory_name, to_copy=to_copy)
                added_torrent = add_torrent_from_tracker(
                    tracker=tracker,
                    tracker_id=tracker_id,
                    download_path_pattern=download_path_pattern,
                    force_fetch=True,
                    store_files_hook=itm.move_files
                )
                
            offset += limit
            snatched = tracker.get_snatched(offset, limit)
    

    def add_arguments(self, parser):
        parser.add_argument(
            '--tracker_name',
            help='Name of tracker, example: redacted',
            type=str,
            required=True
        )        
        parser.add_argument(
            '--source_path_pattern',
            type=str, 
            help='Where to look for torrent contents',
            required=True
        )
        parser.add_argument(
            '--download_path_pattern',
            type=str, 
            help='Where to seed torrent contents from',
            required=True
        )
        parser.add_argument('-add_missing', 
            action='store_true', 
            help='Adds torrents that cannot be found in source_path_pattern',
            default=False
        )
        parser.add_argument(
            '-copy',
            help='Copies files instead of moving them in', 
            action='store_true',
            default=False
        )


    def handle(self, *args, **options):
        tracker_name = options['tracker_name']
        source_path_pattern = options['source_path_pattern']
        download_path_pattern = options['download_path_pattern']
        reject_missing = not options['add_missing']
        to_copy = options['copy']

        tracker = TrackerRegistry.get_plugin(tracker_name, self.__class__.__name__)

        self.add_missing_from_tracker(
            tracker=tracker,
            source_path_pattern=source_path_pattern,
            download_path_pattern=download_path_pattern,
            reject_missing=reject_missing,
            to_copy=to_copy
        )
   