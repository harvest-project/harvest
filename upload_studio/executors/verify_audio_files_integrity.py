import os
import subprocess

from Harvest.utils import get_logger
from upload_studio.audio_utils import AudioDiscoveryStepMixin
from upload_studio.step_executor import StepExecutor

logger = get_logger(__name__)


class VerifyAudioFilesIntegrityExecutor(AudioDiscoveryStepMixin, StepExecutor):
    name = 'verify_audio_files_integrity'
    description = 'Verifies the integrity of audio files.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.num_verified = 0

    def rename_files(self):
        for audio_file in self.audio_files:
            ext = os.path.splitext(audio_file.abs_path)[1]
            if ext == '.flac':
                subprocess.check_call(['flac', '-t', audio_file.abs_path])
            else:
                raise ValueError('Unsupported file format: {}'.format(ext))
            self.num_verified += 1

    def update_metadata(self):
        self.metadata.processing_steps.append(
            'Verified the integrity of {} audio files (e.g. flac -t). Stream config: {}'.format(
                self.num_verified,
                self.stream_info,
            ))

    def handle_run(self):
        self.copy_prev_step_files()
        self.discover_audio_files()
        self.rename_files()
        self.update_metadata()
