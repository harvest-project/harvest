import os

from Harvest.utils import get_logger
from upload_studio.imgur_client import HarvestImgurClient
from upload_studio.step_executor import StepExecutor

logger = get_logger(__name__)

COVER_NAMES = {
    'cover.jpg',
    'cover.jpeg',
    'folder.jpg',
    'folder.jpeg',
}


class UploadCoverToImgurExecutor(StepExecutor):
    name = 'upload_cover_to_imgur'
    description = 'Uploads the cover file (cover.jpg, folder.jpg) to imgur.'

    def find_cover(self):
        for filename in os.listdir(self.step.data_path):
            if filename.lower() in COVER_NAMES:
                return os.path.join(self.step.data_path, filename)

    def upload_cover(self, cover_file):
        self.metadata.cover_url = HarvestImgurClient().upload_image(cover_file)

    def update_metadata(self):
        self.metadata.processing_steps.append(
            'Uploaded cover art to imgur with URL {}'.format(self.metadata.cover_url))

    def handle_run(self):
        self.copy_prev_step_files()
        cover_file = self.find_cover()
        self.upload_cover(cover_file)
        self.update_metadata()
