import os
import re
from itertools import groupby

from Harvest.utils import get_logger
from upload_studio.audio_utils import AudioDiscoveryStepMixin
from upload_studio.step_executor import StepExecutor

logger = get_logger(__name__)


class FixFilenameTrackNumbers(AudioDiscoveryStepMixin, StepExecutor):
    name = 'fix_filename_track_numbers'
    description = 'Fixes bad track numbers in filenames.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.num_renamed = 0

    def rename_files_in_dir(self, files):
        rjust_width = len(str(len(files)))
        for audio_file in files:
            filename = os.path.basename(audio_file.rel_path)
            filename_match = re.match('^([0-9]+).*', filename)
            if not filename_match:
                self.raise_error('Unable to find any track number in file {}.'.format(audio_file.rel_path))
            filename_track = int(filename_match.group(1))

            if filename_track != audio_file.track:
                self.raise_error('Track number mismatch on {}. Filename has {}, tags have {}.'.format(
                    audio_file.rel_path, filename_track, audio_file.track))

            track_str = str(audio_file.track).rjust(rjust_width, '0')
            new_filename = track_str + filename[len(filename_match.group(1)):]

            if new_filename != filename:
                new_abs_path = os.path.join(os.path.dirname(audio_file.abs_path), new_filename)
                logger.info('Renaming {} to {} in order to fix filename track sorting.'.format(
                    audio_file.abs_path, new_abs_path))
                os.rename(audio_file.abs_path, new_abs_path)
                self.num_renamed += 1

    def rename_files(self):
        for dir_path, dir_files in groupby(self.audio_files, lambda f: os.path.dirname(f.abs_path)):
            self.rename_files_in_dir(list(dir_files))

    def update_metadata(self):
        if self.num_renamed:
            self.metadata.processing_steps.append(
                'Renamed {} files so that filename track numbers have proper leading zeros.'.format(
                    self.num_renamed))

    def handle_run(self):
        self.copy_prev_step_files()
        self.discover_audio_files()
        self.rename_files()
        self.update_metadata()
