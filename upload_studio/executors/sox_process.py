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
from files.audio_utils import StreamInfo
from upload_studio.audio_utils import InconsistentStreamInfoException, get_stream_info
from upload_studio.step_executor import StepExecutor
from upload_studio.upload_metadata import MusicMetadata
from upload_studio.utils import execute_subprocess_chain, pprint_subprocess_chain

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
        self.flac_version = None
        self.src_stream_info = None
        self.dst_stream_info = None

    def check_prerequisites(self):
        if self.metadata.format != MusicMetadata.FORMAT_FLAC:
            self.raise_error('Processing files with SoX only supports FLAC input.')

        try:
            self.sox_version = subprocess.check_output(['sox', '--version']).decode().split('\n')[0][4:].strip()
        except FileNotFoundError:
            self.raise_error('sox not found in path. Make sure sox is installed.')

        try:
            self.flac_version = subprocess.check_output(['flac', '--version']).decode().split('\n')[0]
        except FileNotFoundError:
            self.raise_error('flac not found in path. Make sure flac is installed.')

    def _get_dst_stream_info(self):
        src_sample_rate = self.src_stream_info.sample_rate
        src_bits_per_sample = self.src_stream_info.bits_per_sample
        src_channels = self.src_stream_info.channels

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

        if target_sample_rate != src_sample_rate and target_sample_rate * 2 > src_sample_rate:
            self.raise_error('Refusing to resample by less than a factor of 2.')

        requires_processing = (
                target_sample_rate != src_sample_rate or
                src_bits_per_sample != self.target_bits_per_sample or
                src_channels != self.target_channels
        )
        if requires_processing:
            return StreamInfo(
                sample_rate=target_sample_rate,
                bits_per_sample=self.target_bits_per_sample,
                channels=self.target_channels,
            )
        else:
            return None

    def init_audio_files(self):
        self.audio_files = []
        for src_file, dst_file in list_src_dst_files(self.prev_step.data_path, self.step.data_path):
            if src_file.lower().endswith('.flac'):
                self.audio_files.append(self.FileInfo(src_file, dst_file))
            else:
                logger.info('Project {} copying file {} to {}.', self.project.id, src_file, dst_file)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)

        try:
            self.src_stream_info = get_stream_info(f.src_muta for f in self.audio_files)
        except InconsistentStreamInfoException as exc:
            self.raise_error(str(exc))
        self.dst_stream_info = self._get_dst_stream_info()

    def _get_transcoding_chain(self, src_file, dst_file):
        flac_decode_options = ['flac', '-d', '-c', src_file]
        sox_options = [
            'sox',
            '-t', 'wav', '-',
            '-b', str(self.dst_stream_info.bits_per_sample),
            '-t', 'wav', '-',
            'rate', '-v', '-L', str(self.dst_stream_info.sample_rate),
            'dither',
        ]
        flac_encode_options = ['flac', '--best', '-o', dst_file, '-']
        return flac_decode_options, sox_options, flac_encode_options

    def process_audio_files(self):
        for file in self.audio_files:
            chain = self._get_transcoding_chain(file.src_file, file.dst_file)
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
        if not self.dst_stream_info:
            self.metadata.processing_steps.append(
                'Source audio stream is {}, no sample rate/bit depth/channels conversion needed.'.format(
                    self.src_stream_info))
            return
        self.metadata.processing_steps.append(
            'Source audio stream is {}. Convert to {} with {}. Command line: {}.'
            ' Encode back to FLAC with {}.'.format(
                self.src_stream_info,
                self.dst_stream_info,
                self.sox_version,
                pprint_subprocess_chain(self._get_transcoding_chain('{src}', '{dst}')),
                self.flac_version,
            ),
        )
        self.metadata.additional_data['downsample_data'] = {
            'src_sample_rate': self.src_stream_info.sample_rate,
            'src_bits_per_sample': self.src_stream_info.bits_per_sample,
            'src_channels': self.src_stream_info.channels,
            'dst_sample_rate': self.dst_stream_info.sample_rate,
            'dst_bits_per_sample': self.dst_stream_info.bits_per_sample,
            'dst_channels': self.dst_stream_info.channels,
        }
        if self.dst_stream_info.bits_per_sample == 16:
            self.metadata.encoding = MusicMetadata.ENCODING_LOSSLESS
        elif self.dst_stream_info.bits_per_sample == 24:
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
