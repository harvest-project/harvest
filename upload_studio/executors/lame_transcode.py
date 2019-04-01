import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

import mutagen.easyid3
import mutagen.flac
import mutagen.id3
import mutagen.mp3

from Harvest.utils import get_logger
from upload_studio.step_executor import StepExecutor
from upload_studio.upload_metadata import MusicMetadata
from upload_studio.utils import list_src_dst_files, execute_subprocess_chain

logger = get_logger(__name__)

FILES_TO_COPY = {'folder.jpg', 'folder.jpeg', 'cover.jpg', 'cover.jpeg', 'front.jpg', 'front.jpeg', 'front cover.jpg',
                 'front cover.jpeg', 'art.jpg', 'art.jpeg', 'thumbnail.jpg', 'thumbnail.jpeg'}
ALLOWED_SAMPLE_RATES = {44100, 48000}
ALLOWED_BITS_PER_SAMPLE = {16}
ALLOWED_CHANNELS = {2}
LAME_BITRATE_SETTINGS = {
    MusicMetadata.ENCODING_320: ['--cbr', '-b', '320'],
    MusicMetadata.ENCODING_V0: ['-V', '0'],
    MusicMetadata.ENCODING_V2: ['-V', '2'],
}


class LAMETranscoderExecutor(StepExecutor):
    class FileInfo:
        def __init__(self, src_file, dst_file):
            self.src_file = src_file
            self.dst_file = dst_file
            self.src_muta = mutagen.flac.FLAC(self.src_file)

        def copy_tags(self):
            try:
                dst_muta = mutagen.easyid3.EasyID3(self.dst_file)
            except mutagen.id3.ID3NoHeaderError:
                dst_muta = mutagen.File(self.dst_file, easy=True)
                dst_muta.add_tags()
            for tag in self.src_muta:
                if tag in mutagen.easyid3.EasyID3.valid_keys.keys():
                    dst_muta[tag] = self.src_muta[tag]
            dst_muta.save()

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
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)
            elif src_file.endswith('.part'):
                self.raise_error('Refusing to run with a .part file in source directory.')
            elif src_file.lower().endswith('.flac'):
                logger.info('Project {} adding {} for transcoding.', self.project.id, src_file)
                dst_file = dst_file[:-len('.flac')] + '.mp3'
                self.audio_files.append(self.FileInfo(src_file, dst_file))

        if len(self.audio_files) == 0:
            self.raise_error('No FLACs discovered in source directory.')

    def check_audio_files(self):
        for file in self.audio_files:
            sample_rate = file.src_muta.info.sample_rate
            bits_per_sample = file.src_muta.info.bits_per_sample
            channels = file.src_muta.info.channels

            if sample_rate not in ALLOWED_SAMPLE_RATES:
                self.raise_error(
                    '{} only input files with sample rates {} are supported. '
                    'File {} has {}. Run a sox step if needed.'.format(
                        self.project, ALLOWED_SAMPLE_RATES, file.src_file, sample_rate))
            if bits_per_sample not in ALLOWED_BITS_PER_SAMPLE:
                self.raise_error(
                    '{} only input files with bits per sample {} are supported. '
                    'File {} has {}. Run a sox step if needed.'.format(
                        self.project, ALLOWED_BITS_PER_SAMPLE, file.src_file, bits_per_sample))
            if channels not in ALLOWED_CHANNELS:
                self.raise_error(
                    '{} only input files with channels {} are supported. '
                    'File {} has {}. Run a sox stepsif needed.'.format(
                        self.project, ALLOWED_CHANNELS, file.src_file, channels))

    def transcode_audio_files(self):
        chains = []

        for file in self.audio_files:
            flac_options = ['flac', '-d', '-c', file.src_file]
            lame_options = ['lame', '-h']
            if self.bitrate in LAME_BITRATE_SETTINGS:
                lame_options += LAME_BITRATE_SETTINGS[self.bitrate]
            else:
                self.raise_error('{} unknown bitrate {}. Supported bitrates are {}.'.format(
                    self.project, self.bitrate, list(LAME_BITRATE_SETTINGS.keys())))
            lame_options += ['-', file.dst_file]

            chain = (flac_options, lame_options)
            chains.append(chain)
            logger.info('{} transcoding plan {} -> {} with chain {}.'.format(
                self.project, file.src_file, file.dst_file, chain))

            os.makedirs(os.path.dirname(file.dst_file), exist_ok=True)

        max_workers = os.cpu_count()
        executor = ThreadPoolExecutor(max_workers=max_workers)
        logger.info('{} starting transcode processes with {} workers.'.format(self.project, max_workers))
        list(executor.map(execute_subprocess_chain, chains, timeout=300))
        logger.info('{} starting copy tags.'.format(self.project))
        list(executor.map(self.FileInfo.copy_tags, self.audio_files, timeout=300))

    def check_output_files(self):
        for file in self.audio_files:
            if not os.path.isfile(file.dst_file) or os.path.getsize(file.dst_file) < 8196:
                self.raise_error('Missing output file or is less than 8K')

    def update_metadata(self):
        self.metadata.format = MusicMetadata.FORMAT_MP3
        self.metadata.encoding = self.bitrate

    def handle_run(self):
        self.check_prerequisites()
        self.init_audio_files()
        self.check_audio_files()
        self.transcode_audio_files()
        self.check_output_files()
        self.update_metadata()
