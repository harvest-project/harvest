import os
import subprocess
from subprocess import CalledProcessError

import bencode

from Harvest.path_utils import list_abs_files
from Harvest.utils import get_logger
from trackers.utils import TorrentFileInfo
from upload_studio.step_executor import StepExecutor

logger = get_logger(__name__)

BAD_FILES = {'thumbs.db'}


class CreateTorrentFileExecutor(StepExecutor):
    name = 'create_torrent_files'
    description = 'Creates a .torrent file.'

    def __init__(self, *args, announce, extra_info_keys=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.announce = announce
        self.extra_info_keys = extra_info_keys

    @property
    def torrent_file_path(self):
        return os.path.join(self.step.get_area_path('torrent_file'), self.metadata.torrent_name + '.torrent')

    def check_prerequisites(self):
        try:
            self.mktorrent_version = subprocess.check_output(['mktorrent', '--help']).decode().split('\n')[0]
        except FileNotFoundError:
            self.raise_error('mktorrent not found in path. Make sure mktorrent is installed.')

    def clean_temp_hidden_files(self):
        for file in list_abs_files(self.step.data_path):
            if os.path.basename(file).startswith('.') or file.lower() in BAD_FILES:
                logger.info('{} removing bad file {}.', self.project, file)
                os.remove(file)

    def create_torrent(self):
        os.makedirs(os.path.dirname(self.torrent_file_path), exist_ok=True)
        args = [
            'mktorrent',
            '-a', self.announce,
            '-p',
            '-n', self.metadata.torrent_name,
            '-o', self.torrent_file_path,
            self.step.data_path
        ]
        logger.info('{} creating .torrent file with command: {}', self.project, args)
        try:
            subprocess.check_output(args, encoding='utf-8', stderr=subprocess.STDOUT)
        except CalledProcessError as exc:
            raise Exception('mktorrent failed with code {}: {}'.format(exc.returncode, exc.stdout.strip()))

    def add_extra_info_keys(self):
        if not self.extra_info_keys:
            return
        logger.info('{} adding extra info keys {}.', self.project, self.extra_info_keys)
        with open(self.torrent_file_path, 'rb') as f:
            meta_info = bencode.bdecode(f.read())
        meta_info['info'].update(self.extra_info_keys)
        with open(self.torrent_file_path, 'wb') as f:
            f.write(bencode.bencode(meta_info))

    def record_additional_metadata(self):
        torrent_file_info = TorrentFileInfo.from_file(self.torrent_file_path)
        self.metadata.torrent_info_hash = torrent_file_info.info_hash

    def handle_run(self):
        self.check_prerequisites()
        self.copy_prev_step_files()
        self.clean_temp_hidden_files()
        self.create_torrent()
        self.add_extra_info_keys()
        self.record_additional_metadata()
