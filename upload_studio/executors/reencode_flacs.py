import os
import shutil
from concurrent.futures import ThreadPoolExecutor

import mutagen.easyid3
import mutagen.flac
import mutagen.id3
import mutagen.mp3

from Harvest.path_utils import list_src_dst_files
from Harvest.utils import get_logger
from upload_studio.executors.utils import get_flac_version
from upload_studio.step_executor import StepExecutor
from upload_studio.upload_metadata import MusicMetadata
from upload_studio.utils import execute_subprocess_chain

logger = get_logger(__name__)


class ReencodeFLACsExecutor(StepExecutor):
    class FileInfo:
        def __init__(self, src_file, dst_file, processing_chain):
            self.src_file = src_file
            self.dst_file = dst_file
            self.processing_chain = processing_chain

        def copy_tags(self):
            src_muta = mutagen.File(self.src_file)
            dst_muta = mutagen.File(self.dst_file)
            for tag, value in src_muta.items():
                dst_muta[tag] = value
            dst_muta.save()

        def process(self):
            os.makedirs(os.path.dirname(self.dst_file), exist_ok=True)
            execute_subprocess_chain(self.processing_chain)
            self.copy_tags()

    name = 'reencode_flacs'
    description = 'Decodes and encodes all FLACs.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.flac_version = None
        self.audio_files = None
        self.non_audio_files = None
        self.src_stream_info = None

    def check_prerequisites(self):
        if self.metadata.format != MusicMetadata.FORMAT_FLAC:
            self.raise_error('The FLAC re-encoder currently only supports FLAC input.')

        try:
            self.flac_version = get_flac_version()
        except FileNotFoundError:
            self.raise_error('flac not found in path. Make sure flac is installed.')

    def init_audio_files(self):
        self.audio_files = []
        self.non_audio_files = []
        for src_file, dst_file in list_src_dst_files(self.prev_step.data_path, self.step.data_path):
            if src_file.lower().endswith('.flac'):
                processing_chain = self._get_encoding_chain(src_file, dst_file)
                logger.info('{} re-encoding plan {} -> {} with chain {}.'.format(
                    self.project, src_file, dst_file, processing_chain))

                self.audio_files.append(self.FileInfo(src_file, dst_file, processing_chain))
            elif src_file.endswith('.part'):
                self.raise_error('Refusing to run with a .part file in source directory.')
            else:
                logger.info('Project {} copying file {} to {}.', self.project.id, src_file,
                            dst_file)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)
                self.non_audio_files.append(os.path.relpath(dst_file, self.step.data_path))

        if len(self.audio_files) == 0:
            self.raise_error('No FLACs discovered in source directory.')

    def _get_encoding_chain(self, src_file, dst_file):
        flac_options = ['flac', '-d', '-c', src_file]
        lame_options = ['flac', '--best', '-o', dst_file, '-']
        return flac_options, lame_options

    def transcode_audio_files(self):
        max_workers = os.cpu_count()
        executor = ThreadPoolExecutor(max_workers=max_workers)
        logger.info(
            '{} starting transcode processes with {} workers.'.format(self.project, max_workers))
        list(executor.map(self.FileInfo.process, self.audio_files, timeout=1200))

    def check_output_files(self):
        for file in self.audio_files:
            dst_size = os.path.getsize(file.dst_file)
            if not os.path.isfile(file.dst_file):
                self.raise_error('Missing output file {}.'.format(file.src_file))
            elif dst_size < 8196:
                src_size = os.path.getsize(file.src_file)
                msg = 'Output file {} is small ({} bytes). Input is {} bytes.'.format(
                    file.src_file, dst_size, src_size)
                if src_size < 32768:
                    self.add_warning(msg)
                else:
                    self.raise_error(msg)

    def update_metadata(self):
        self.metadata.processing_steps.append(
            'Re-encoded {} source files with {} and copied {} files.'.format(
                len(self.audio_files),
                self.flac_version,
                len(self.non_audio_files),
            ))

    def handle_run(self):
        self.check_prerequisites()
        self.copy_prev_step_files(exclude_areas={'data'})
        self.init_audio_files()
        self.transcode_audio_files()
        self.check_output_files()
        self.update_metadata()
