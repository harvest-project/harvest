import os
import shutil
from concurrent.futures import ThreadPoolExecutor

import mutagen.easyid3
import mutagen.flac
import mutagen.id3
import mutagen.mp3

from Harvest.path_utils import list_src_dst_files
from Harvest.utils import get_logger
from upload_studio.audio_utils import InconsistentStreamInfoException, get_stream_info
from upload_studio.executors.utils import get_flac_version, get_lame_version
from upload_studio.step_executor import StepExecutor
from upload_studio.upload_metadata import MusicMetadata
from upload_studio.utils import execute_subprocess_chain, pprint_subprocess_chain

logger = get_logger(__name__)

FILES_TO_COPY = {'folder.jpg', 'folder.jpeg', 'cover.jpg', 'cover.jpeg', 'front.jpg', 'front.jpeg',
                 'front cover.jpg',
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
            self.processing_chain = None

        def copy_tags(self):
            dst_muta = mutagen.File(self.dst_file, easy=True)
            for tag in self.src_muta:
                if tag in mutagen.easyid3.EasyID3.valid_keys.keys():
                    dst_muta[tag] = self.src_muta[tag]
            dst_muta.save()

        def process(self):
            os.makedirs(os.path.dirname(self.dst_file), exist_ok=True)
            execute_subprocess_chain(self.processing_chain)
            self.copy_tags()

    name = 'lame_transcode'
    description = 'Transcode lossless files to MP3 using lame.'

    def __init__(self, *args, bitrate, **kwargs):
        super().__init__(*args, **kwargs)
        self.bitrate = bitrate

        self.lame_version = None
        self.flac_version = None
        self.audio_files = None
        self.non_audio_files = None
        self.src_stream_info = None

    def check_prerequisites(self):
        if self.metadata.format != MusicMetadata.FORMAT_FLAC:
            self.raise_error('The LAME encoder currently only supports FLAC input.')

        try:
            self.lame_version = get_lame_version()
        except FileNotFoundError:
            self.raise_error('lame not found in path. Make sure lame is installed.')

        try:
            self.flac_version = get_flac_version()
        except FileNotFoundError:
            self.raise_error('flac not found in path. Make sure flac is installed.')

    def init_audio_files(self):
        self.audio_files = []
        self.non_audio_files = []
        for src_file, dst_file in list_src_dst_files(self.prev_step.data_path, self.step.data_path):
            if os.path.basename(src_file) in FILES_TO_COPY:
                logger.info('Project {} copying file {} to {}.', self.project.id, src_file,
                            dst_file)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)
                self.non_audio_files.append(os.path.relpath(dst_file, self.step.data_path))
            elif src_file.endswith('.part'):
                self.raise_error('Refusing to run with a .part file in source directory.')
            elif src_file.lower().endswith('.flac'):
                logger.info('Project {} adding {} for transcoding.', self.project.id, src_file)
                dst_file = dst_file[:-len('.flac')] + '.mp3'
                self.audio_files.append(self.FileInfo(src_file, dst_file))

        if len(self.audio_files) == 0:
            self.raise_error('No FLACs discovered in source directory.')

    def check_audio_files(self):
        try:
            self.src_stream_info = get_stream_info(f.src_muta for f in self.audio_files)
        except InconsistentStreamInfoException as exc:
            self.raise_error(str(exc))

        if self.src_stream_info.sample_rate not in ALLOWED_SAMPLE_RATES:
            self.raise_error(
                'Files with sample rate {} are not supported, only {}. Run a sox step if needed.'.format(
                    ALLOWED_SAMPLE_RATES, self.src_stream_info.sample_rate))
        if self.src_stream_info.bits_per_sample not in ALLOWED_BITS_PER_SAMPLE:
            self.raise_error(
                'Files with bits per sample {} are not supported, only {}. Run a sox step if needed.'.format(
                    ALLOWED_BITS_PER_SAMPLE, self.src_stream_info.bits_per_sample))
        if self.src_stream_info.channels not in ALLOWED_CHANNELS:
            self.raise_error(
                'Files with channels {} are not supported, only {}. Run a sox step if needed.'.format(
                    ALLOWED_CHANNELS, self.src_stream_info.channels))

    def _get_transcoding_chain(self, src_file, dst_file):
        flac_options = ['flac', '-d', '-c', src_file]
        lame_options = ['lame', '-h']
        if self.bitrate in LAME_BITRATE_SETTINGS:
            lame_options += LAME_BITRATE_SETTINGS[self.bitrate]
        else:
            self.raise_error('Unknown bitrate {}. Supported bitrates are {}.'.format(
                self.bitrate, list(LAME_BITRATE_SETTINGS.keys())))
        lame_options += ['-', dst_file]

        return flac_options, lame_options

    def transcode_audio_files(self):
        for file in self.audio_files:
            file.processing_chain = self._get_transcoding_chain(file.src_file, file.dst_file)
            logger.info('{} transcoding plan {} -> {} with chain {}.'.format(
                self.project, file.src_file, file.dst_file, file.processing_chain))

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
            'Convert source files with audio stream {} to MP3 {} with {}. Command line is {}.'
            ' Include {} audio and {} non-audio files'.format(
                self.src_stream_info,
                self.bitrate,
                self.lame_version,
                pprint_subprocess_chain(self._get_transcoding_chain('{src}', '{dst}')),
                len(self.audio_files),
                len(self.non_audio_files),
            ),
        )
        self.metadata.format = MusicMetadata.FORMAT_MP3
        self.metadata.encoding = self.bitrate

    def handle_run(self):
        self.check_prerequisites()
        self.copy_prev_step_files(exclude_areas={'data'})
        self.init_audio_files()
        self.check_audio_files()
        self.transcode_audio_files()
        self.check_output_files()
        self.update_metadata()
