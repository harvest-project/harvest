from imgurpython import ImgurClient

from upload_studio.models import ImgurConfig


class HarvestImgurClient:
    def __init__(self):
        try:
            self.config = ImgurConfig.objects.get()
        except ImgurConfig.DoesNotExist:
            raise ValueError('Imgur must be configured in the database before using.')
        self.client = ImgurClient(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
        )

    def upload_image(self, image_path):
        credits = self.client.get_credits()
        if credits['UserRemaining'] < 30 or credits['ClientRemaining'] < 30:
            raise Exception('Insufficient imgur credits')

        result = self.client.upload_from_path(image_path)
        return result['link']
