import os
from math import ceil, log10

from Harvest.path_utils import strip_invalid_path_characters
from Harvest.utils import get_logger
from upload_studio.audio_utils import AudioDiscoveryStepMixin
from upload_studio.step_executor import StepExecutor

logger = get_logger(__name__)


class RenameFilesToTags(AudioDiscoveryStepMixin, StepExecutor):
    name = 'rename_files_to_tags'
    description = 'Renames files based on audio file tags'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filename_mapping = {}

    def rename_files(self):
        num_discs = len({a.disc for a in self.audio_files})
        num_tracks = len({a.track for a in self.audio_files})
        disc_len = ceil(log10(num_discs + 1))
        track_len = ceil(log10(num_tracks + 1))

        for audio_file in self.audio_files:
            ext = os.path.splitext(audio_file.abs_path)[1]  # Includes .
            if num_discs > 1:
                new_filename = '{}-{}. {}{}'.format(
                    str(audio_file.disc).zfill(disc_len),
                    str(audio_file.track).zfill(track_len),
                    strip_invalid_path_characters(audio_file.muta.title),
                    ext,
                )
            else:
                new_filename = '{}. {}{}'.format(
                    str(audio_file.track).zfill(track_len),
                    strip_invalid_path_characters(audio_file.muta['title']),
                    ext,
                )

            os.rename(
                audio_file.abs_path,
                os.path.join(self.step.data_path, new_filename)
            )
            self.filename_mapping[audio_file.rel_path] = new_filename

        # Remove all now-empty directories
        for filename in os.listdir(self.step.data_path):
            path = os.path.join(self.step.data_path, filename)
            if os.path.isdir(path):
                try:
                    os.rmdir(path)
                except OSError:
                    pass

    def update_metadata(self):
        self.metadata.processing_steps.append(
            'Fixed filenames by renaming the files based on tags (track numbers and titles).')

    def handle_run(self):
        self.copy_prev_step_files()
        self.discover_audio_files()
        self.rename_files()
        self.update_metadata()

        self.add_warning('Renaming complete. Please confirm filenames:\n\n{}'.format(
            '\n\n'.join('{}\n- {}'.format(*item) for item in self.filename_mapping.items())))
        self.raise_warnings()
