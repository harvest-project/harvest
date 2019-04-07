import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

import mutagen.easyid3
import mutagen.flac
import mutagen.id3
import mutagen.mp3

from Harvest.path_utils import list_src_dst_files
from Harvest.utils import get_logger
from upload_studio.step_executor import StepExecutor
from upload_studio.upload_metadata import MusicMetadata
from upload_studio.utils import execute_subprocess_chain

logger = get_logger(__name__)


class SoxProcessExecutor(StepExecutor):
    TARGET_SAMPLE_RATE_44100_OR_4800 = '44100/4800'

    class FileInfo:
        def __init__(self, src_file, dst_file):
            self.src_file = src_file
            self.dst_file = dst_file
            self.src_muta = mutagen.flac.FLAC(self.src_file)
            self.processing_chain = None

        def copy_tags(self):
            dst_muta = mutagen.flac.FLAC(self.dst_file)
            for tag in self.src_muta:
                dst_muta[tag] = self.src_muta[tag]
            dst_muta.save()

        def process(self):
            os.makedirs(os.path.dirname(self.dst_file), exist_ok=True)
            execute_subprocess_chain(self.processing_chain)
            self.copy_tags()

    name = 'sox_process'
    description = 'Run files through sox, if channels/sample rate/bit depth need changing.'

    def __init__(self, *args, target_sample_rate, target_bits_per_sample, target_channels, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_sample_rate = target_sample_rate
        self.target_bits_per_sample = target_bits_per_sample
        self.target_channels = target_channels

        self.audio_files = None
        self.sox_version = None
        self.src_stream_info = None
        self.dst_stream_info = None

    def check_prerequisites(self):
        if self.metadata.format != MusicMetadata.FORMAT_FLAC:
            self.raise_error('Processing files with SoX only supports FLAC input.')

        try:
            self.sox_version = subprocess.check_output(['sox', '--version']).decode().split('\n')[0][4:].strip()
        except FileNotFoundError:
            self.raise_error('sox not found in path. Make sure sox is installed.')

    def _get_dst_stream_info(self):
        src_sample_rate, src_bits_per_sample, src_channels = self.src_stream_info

        if self.target_sample_rate == self.TARGET_SAMPLE_RATE_44100_OR_4800:
            if src_sample_rate == 44100 or src_sample_rate >= 88200:
                target_sample_rate = 44100
            elif src_sample_rate == 48000:
                target_sample_rate = 48000
            else:
                self.raise_error('Unable to find good target sample rate for sample rate of {}'.format(src_sample_rate))
        else:
            target_sample_rate = self.target_sample_rate

        if src_channels != self.target_channels:
            self.raise_error('sox_process does not currently support remixing channels safely.')

        requires_processing = (
                target_sample_rate != src_sample_rate or
                src_bits_per_sample != self.target_bits_per_sample or
                src_channels != self.target_channels
        )
        if requires_processing:
            if target_sample_rate * 2 > src_sample_rate:
                self.raise_error('Refusing to resample by less than a factor of 2.')
            return target_sample_rate, self.target_bits_per_sample, self.target_channels
        else:
            return None

    def init_audio_files(self):
        self.audio_files = []
        for src_file, dst_file in list_src_dst_files(self.prev_step.data_path, self.step.data_path):
            if src_file.lower().endswith('.flac'):
                file = self.FileInfo(src_file, dst_file)
                src_stream_info = (
                    file.src_muta.info.sample_rate,
                    file.src_muta.info.bits_per_sample,
                    file.src_muta.info.channels,
                )
                if self.src_stream_info is None:
                    self.src_stream_info = src_stream_info
                if self.src_stream_info != src_stream_info:
                    self.raise_error('sox_process does not currently support heterogeneous torrents.')
                self.audio_files.append(file)
            else:
                logger.info('Project {} copying file {} to {}.', self.project.id, src_file, dst_file)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)

        self.dst_stream_info = self._get_dst_stream_info()

    def process_audio_files(self):
        for file in self.audio_files:
            flac_decode_options = ['flac', '-d', '-c', file.src_file]
            sox_options = [
                'sox',
                '-t', 'wav', '-',
                '-b', str(self.dst_stream_info[1]),
                '-t', 'wav', '-',
                'rate', '-v', '-L',
                str(self.dst_stream_info[0]),
                'dither',
            ]
            flac_encode_options = ['flac', '--best', '-o', file.dst_file, '-']
            chain = (flac_decode_options, sox_options, flac_encode_options)
            file.processing_chain = chain
            logger.info('{} transcoding plan {} -> {} with chain {}.'.format(
                self.project, file.src_file, file.dst_file, chain))

        max_workers = os.cpu_count()
        executor = ThreadPoolExecutor(max_workers=max_workers)
        logger.info('{} starting processes with {} workers.'.format(self.project, max_workers))
        list(executor.map(self.FileInfo.process, self.audio_files, timeout=300))

    def copy_audio_files(self):
        for file in self.audio_files:
            logger.info('Project {} copying file {} to {}.', self.project.id, file.src_file, file.dst_file)
            os.makedirs(os.path.dirname(file.dst_file), exist_ok=True)
            shutil.copy2(file.src_file, file.dst_file)

    def check_output_files(self):
        for file in self.audio_files:
            if not os.path.isfile(file.dst_file) or os.path.getsize(file.dst_file) < 8196:
                self.raise_error('Missing output file or is less than 8K')

    def update_metadata(self):
        self.metadata.additional_data['downsample_data'] = {
            'src_sample_rate': self.src_stream_info[0],
            'src_bits_per_sample': self.src_stream_info[1],
            'src_channels': self.src_stream_info[2],
            'dst_sample_rate': self.dst_stream_info[0],
            'dst_bits_per_sample': self.dst_stream_info[1],
            'dst_channels': self.dst_stream_info[2],
        }
        if self.dst_stream_info[1] == 16:
            self.metadata.encoding = MusicMetadata.ENCODING_LOSSLESS
        elif self.dst_stream_info[1] == 24:
            self.metadata.encoding = MusicMetadata.ENCODING_24BIT_LOSSLESS
        else:
            self.raise_error('Metadata only supports 16 and 24 bit output bit depths.')

    def handle_run(self):
        self.check_prerequisites()
        self.copy_prev_step_files(exclude_areas={'data'})
        self.init_audio_files()
        if self.dst_stream_info:
            self.process_audio_files()
        else:
            self.copy_audio_files()
        self.check_output_files()
        self.update_metadata()
