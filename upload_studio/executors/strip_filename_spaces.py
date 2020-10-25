import os

from Harvest.utils import get_logger
from upload_studio.audio_utils import AudioDiscoveryStepMixin
from upload_studio.step_executor import StepExecutor

logger = get_logger(__name__)


class StripFilenameSpaces(AudioDiscoveryStepMixin, StepExecutor):
    name = 'strip_filename_spaces'
    description = 'Strips leading and trailing spaces from filenames.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.num_renamed = 0

    def rename_files(self):
        for audio_file in self.audio_files:
            filename = os.path.basename(audio_file.rel_path)
            new_filename = filename.strip()

            if filename != new_filename:
                new_abs_path = os.path.join(os.path.dirname(audio_file.abs_path), new_filename)
                logger.info('Renaming {} to {} in order to fix filename spaces.'.format(
                    audio_file.abs_path, new_abs_path))
                os.rename(audio_file.abs_path, new_abs_path)
                self.num_renamed += 1

    def update_metadata(self):
        if self.num_renamed:
            self.metadata.processing_steps.append(
                'Renamed {} files so that filename have no leading or trailing spaces.'.format(
                    self.num_renamed))

    def handle_run(self):
        self.copy_prev_step_files()
        self.discover_audio_files()
        self.rename_files()
        self.update_metadata()
