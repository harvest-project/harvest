import os
import shutil
import subprocess

import mutagen.flac

from Harvest.utils import get_logger
from upload_studio.step_executor import StepExecutor
from upload_studio.upload_metadata import MusicMetadata
from upload_studio.utils import list_src_dst_files

logger = get_logger(__name__)

FILES_TO_COPY = {'folder.jpg', 'folder.jpeg', 'cover.jpg', 'cover.jpeg', 'front.jpg', 'front.jpeg', 'front cover.jpg',
                 'front cover.jpeg', 'art.jpg', 'art.jpeg'}
ALLOWED_SAMPLE_RATES = {44100, 48000}
ALLOWED_BITS_PER_SAMPLE = {16}
ALLOWED_CHANNELS = {2}


class LAMETranscoderExecutor(StepExecutor):
    class FileInfo:
        def __init__(self, src_file, dst_file):
            self.src_file = src_file
            self.dst_file = dst_file
            self.muta = mutagen.flac.FLAC(self.src_file)

    name = 'lame_transcode'
    description = 'Transcode lossless files to MP3 using lame.'

    def __init__(self, *args, bitrate, **kwargs):
        super().__init__(*args, **kwargs)
        self.bitrate = bitrate

        self.lame_version = None
        self.flac_version = None
        self.audio_files = None

    def check_prerequisites(self):
        if self.metadata.format != MusicMetadata.FORMAT_FLAC:
            self.raise_error('The LAME encoder currently only supports FLAC input.')

        try:
            self.lame_version = subprocess.check_output(['lame', '--version']).decode().split('\n')[0]
        except FileNotFoundError:
            self.raise_error('lame not found in path. Make sure lame is installed.')

        try:
            self.flac_version = subprocess.check_output(['flac', '--version']).decode().split('\n')[0]
        except FileNotFoundError:
            self.raise_error('flac not found in path. Make sure flac is installed.')

    def init_audio_files(self):
        self.audio_files = []
        for src_file, dst_file in list_src_dst_files(self.prev_step.data_path, self.step.data_path):
            if os.path.basename(src_file) in FILES_TO_COPY:
                logger.info('Project {} copying file {} to {}.', self.project.id, src_file, dst_file)
                shutil.copy2(src_file, dst_file)
            elif src_file.endswith('.part'):
                self.raise_error('Refusing to run with a .part file in source directory.')
            elif src_file.lower().endswith('.flac'):
                logger.info('Project {} adding {} for transcoding.', self.project.id, src_file)
                self.audio_files.append(self.FileInfo(src_file, dst_file))

        if len(self.audio_files) == 0:
            self.raise_error('No FLACs discovered in source directory.')

    def check_audio_files(self):
        for file in self.audio_files:
            if file.muta.info.sample_rate not in ALLOWED_SAMPLE_RATES:
                self.raise_error(
                    '{} only input files with sample rates {} are supported. '
                    'File {} has {}. Run a sox step if needed.'.format(
                        self.project, ALLOWED_SAMPLE_RATES, file.src_file, file.muta.info.sample_rate))
            if file.muta.info.bits_per_sample not in ALLOWED_BITS_PER_SAMPLE:
                self.raise_error(
                    '{} only input files with bits per sample {} are supported. '
                    'File {} has {}. Run a sox step if needed.'.format(
                        self.project, ALLOWED_BITS_PER_SAMPLE, file.src_file, file.muta.info.bits_per_sample))
            if file.muta.info.channels not in ALLOWED_CHANNELS:
                self.raise_error(
                    '{} only input files with channels {} are supported. '
                    'File {} has {}. Run a sox stepsif needed.'.format(
                        self.project, ALLOWED_CHANNELS, file.src_file, file.muta.info.channels))

    def handle_run(self):
        self.check_prerequisites()
        self.clean_work_area()
        self.init_audio_files()
        self.check_audio_files()
        raise NotImplementedError()
