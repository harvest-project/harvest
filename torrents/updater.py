import logging

from torrents.alcazar_client import AlcazarClient
from torrents.exceptions import AlcazarNotConfiguredException

logger = logging.getLogger(__name__)


class AlcazarUpdater:
    def __init__(self):
        try:
            client = AlcazarClient()
        except AlcazarNotConfiguredException:
            logger.info('Skipping alcazar poll due to missing config.')
            return

    def run(self):
        pass
