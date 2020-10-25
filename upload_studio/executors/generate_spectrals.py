import os
import subprocess
from concurrent.futures.thread import ThreadPoolExecutor

from PIL import Image

from Harvest.utils import get_logger
from upload_studio.audio_utils import AudioDiscoveryStepMixin
from upload_studio.step_executor import StepExecutor

logger = get_logger(__name__)


def time_text(seconds):
    if type(seconds) == float:
        seconds = int(seconds)
    assert type(seconds) == int
    return u'{0}:{1:02}'.format(seconds // 60, seconds % 60)


class GenerateSpectralsExecutor(AudioDiscoveryStepMixin, StepExecutor):
    name = 'generate_spectrals'
    description = 'Generates spectral images.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.spectrals_path = self.step.get_area_path('spectrals')

    def check_prerequisites(self):
        try:
            self.sox_version = subprocess.check_output(['sox', '--version']).decode().split('\n')[0]
        except FileNotFoundError:
            self.raise_error('sox not found in path. Make sure sox is installed.')

    def create_spectrals_for_file(self, audio_file):
        basename = os.path.splitext(os.path.basename(audio_file.abs_path))[0]
        full_filename = os.path.join(self.spectrals_path, u'{0}.full.png'.format(basename))
        zoom_filename = os.path.join(self.spectrals_path, u'{0}.zoom.png'.format(basename))
        spectral_filename = os.path.join(self.spectrals_path, u'{0}.png'.format(basename))

        full_title = '{0} Full'.format(os.path.splitext(audio_file.abs_path)[0])
        zoom_title = '{0} Zoom'.format(os.path.splitext(audio_file.abs_path)[0])

        full_args = [
            'sox', audio_file.abs_path, '-n', 'remix', '1', 'spectrogram', '-x', '2000', '-y',
            '513', '-w', 'Kaiser', '-t', full_title, '-o', full_filename
        ]
        subprocess.check_call(full_args)

        zoom_start = time_text(min(40, audio_file.duration - 10))
        zoom_args = [
            'sox', audio_file.abs_path, '-n', 'remix', '1', 'spectrogram', '-x', '2000', '-y',
            '513', '-w', 'Kaiser', '-S', zoom_start, '-d', '0:04', '-t', zoom_title, '-o',
            zoom_filename,
        ]
        subprocess.check_call(zoom_args)

        self._merge_images(spectral_filename, (full_filename, zoom_filename))
        os.remove(full_filename)
        os.remove(zoom_filename)

    def create_spectrals(self):
        os.makedirs(self.spectrals_path, exist_ok=True)

        max_workers = os.cpu_count()
        executor = ThreadPoolExecutor(max_workers=max_workers)
        list(executor.map(self.create_spectrals_for_file, self.audio_files, timeout=1200))

    def record_additional_metadata(self):
        self.metadata.processing_steps.append('Generate spectral images using sox.')

    def handle_run(self):
        self.check_prerequisites()
        self.copy_prev_step_files()
        self.discover_audio_files()
        self.create_spectrals()
        self.record_additional_metadata()

    @staticmethod
    def _merge_images(target_path, source_paths):
        images = list(map(Image.open, source_paths))
        try:
            result_width = max(i.size[0] for i in images)
            result_height = sum(i.size[1] for i in images)
            result = Image.new('P', (result_width, result_height))
            result.putpalette(images[0].getpalette())
            current_y = 0
            for image in images:
                result.paste(image, (0, current_y, image.size[0], current_y + image.size[1]))
                current_y += image.size[1]
            result.save(target_path, 'PNG')
        finally:
            for image in images:
                image.close()
