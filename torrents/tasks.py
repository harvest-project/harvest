import logging

from django.db import transaction
from huey.contrib.djhuey import db_periodic_task, lock_task

from Harvest.huey_scheduler import IntervalSeconds
from torrents.alcazar_client import AlcazarClient
from torrents.alcazar_event_processor import AlcazarEventProcessor
from torrents.exceptions import AlcazarNotConfiguredException

logger = logging.getLogger(__name__)


@db_periodic_task(IntervalSeconds(3))
@transaction.atomic
@lock_task('poll_alcazar')
def poll_alcazar():
    try:
        client = AlcazarClient(timeout=60)
    except AlcazarNotConfiguredException:
        logger.info('Skipping alcazar poll due to missing config.')
        return

    events = client.pop_updates()
    # print(events)

    logger.debug('Received {} updates and {} deletes from alcazar.'.format(
        len(events['updated']), len(events['removed'])))

    processor = AlcazarEventProcessor()
    processor.process(events)
