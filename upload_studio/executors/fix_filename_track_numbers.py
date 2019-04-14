import os
import re
from itertools import groupby

from Harvest.utils import get_logger
from upload_studio.audio_utils import AudioDiscoveryStepMixin
from upload_studio.step_executor import StepExecutor

logger = get_logger(__name__)


class FixFilenameTrackNumbers(AudioDiscoveryStepMixin, StepExecutor):
    class FilenameTrackMatch:
        def __init__(self, audio_file):
            self.filename = os.path.basename(audio_file.rel_path)
            self.filename_match = re.match('^([0-9]+).*', self.filename)
            if not self.filename_match:
                raise Exception('Unable to find any track number in file {}.'.format(audio_file.rel_path))
            self.filename_track = int(self.filename_match.group(1))
            if self.filename_track != audio_file.track:
                raise Exception('Track number mismatch on {}. Filename has {}, tags have {}.'.format(
                    audio_file.rel_path, self.filename_track, audio_file.track))

    name = 'fix_filename_track_numbers'
    description = 'Fixes bad track numbers in filenames.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.num_renamed = 0

    def discover_audio_files(self):
        super().discover_audio_files()
        for audio_file in self.audio_files:
            audio_file.track_match = self.FilenameTrackMatch(audio_file)

    def rename_files_in_dir(self, files):
        max_track = max(f.track_match.filename_track for f in files)
        rjust_width = len(str(max_track))

        for audio_file in files:
            match = audio_file.track_match

            track_str = str(audio_file.track).rjust(rjust_width, '0')
            new_filename = track_str + match.filename[len(match.filename_match.group(1)):]

            if new_filename != match.filename:
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
