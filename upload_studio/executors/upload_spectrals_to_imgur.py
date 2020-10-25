from Harvest.path_utils import list_abs_files
from Harvest.utils import get_logger
from upload_studio.imgur_client import HarvestImgurClient
from upload_studio.step_executor import StepExecutor

logger = get_logger(__name__)


class UploadSpectralsImgurExecutor(StepExecutor):
    name = 'upload_spectrals_to_imgur'
    description = 'Uploads the spectral images to imgur.'

    def upload_spectrals(self):
        if self.step.projectstepwarning_set.exists():
            # Images are already uploaded, don't reupload
            return

        imgur_client = HarvestImgurClient()
        urls = []
        for spectral_path in list_abs_files(self.step.get_area_path('spectrals')):
            urls.append(imgur_client.upload_image(spectral_path))
        self.add_warning('Spectral URLs:\n{}'.format('\n'.join(urls)))

    def handle_run(self):
        self.copy_prev_step_files()
        self.upload_spectrals()
        self.raise_warnings()
