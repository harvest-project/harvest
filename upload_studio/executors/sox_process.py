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
            self.dst_stream_info = None
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

    def check_prerequisites(self):
        if self.metadata.format != MusicMetadata.FORMAT_FLAC:
            self.raise_error('Processing files with SoX only supports FLAC input.')

        try:
            self.sox_version = subprocess.check_output(['sox', '--version']).decode().split('\n')[0][4:].strip()
        except FileNotFoundError:
            self.raise_error('sox not found in path. Make sure sox is installed.')

    def _get_target_stream_info(self, sample_rate, bits_per_sample, channels):
        if self.target_sample_rate == self.TARGET_SAMPLE_RATE_44100_OR_4800:
            if sample_rate % 44100 == 0:
                target_sample_rate = 44100
            elif sample_rate % 48000 == 0:
                target_sample_rate = 48000
            else:
                self.raise_error('Unable to find good target sample rate for sample rate of {}'.format(sample_rate))
        else:
            target_sample_rate = self.target_sample_rate

        if channels != self.target_channels:
            self.raise_error('sox_process does not currently support remixing channels safely.')

        requires_processing = (
                target_sample_rate != sample_rate or
                bits_per_sample != self.target_bits_per_sample or
                channels != self.target_channels
        )
        if requires_processing:
            return target_sample_rate, self.target_bits_per_sample, self.target_channels
        else:
            return None

    def init_audio_files(self):
        self.audio_files = []
        for src_file, dst_file in list_src_dst_files(self.prev_step.data_path, self.step.data_path):
            if src_file.lower().endswith('.flac'):
                file = self.FileInfo(src_file, dst_file)
                dst_stream_info = self._get_target_stream_info(
                    file.src_muta.info.sample_rate,
                    file.src_muta.info.bits_per_sample,
                    file.src_muta.info.channels,
                )
                if dst_stream_info:
                    file.dst_stream_info = dst_stream_info
                    logger.info('Project {} adding {} for sox processing.', self.project.id, src_file)
                    self.audio_files.append(file)
                    continue
            logger.info('Project {} copying file {} to {}.', self.project.id, src_file, dst_file)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)

    def process_audio_files(self):
        for file in self.audio_files:
            flac_decode_options = ['flac', '-d', '-c', file.src_file]
            sox_options = [
                'sox',
                '-t', 'wav', '-',
                '-b', str(file.dst_stream_info[1]),
                '-t', 'wav', '-',
                'rate', '-v', '-L',
                str(file.dst_stream_info[0]),
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

    def check_output_files(self):
        for file in self.audio_files:
            if not os.path.isfile(file.dst_file) or os.path.getsize(file.dst_file) < 8196:
                self.raise_error('Missing output file or is less than 8K')

    def handle_run(self):
        self.check_prerequisites()
        self.copy_prev_step_files(exclude_areas={'data'})
        self.init_audio_files()
        self.process_audio_files()
        self.check_output_files()
