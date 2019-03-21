import logging
from time import sleep

from django.db import models, transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class ThrottledRequest(models.Model):
    datetime = models.DateTimeField()

    class Meta:
        abstract = True


class DatabaseSyncedThrottler:
    def __init__(self, model, num_requests, per_seconds):
        self.model = model
        self.num_requests = num_requests
        self.per_seconds = per_seconds

    @transaction.atomic
    def throttle_request(self, **request_params):
        requests = list(self.model.objects.select_for_update().order_by('datetime'))

        current_datetime = timezone.now()
        if len(requests) >= self.num_requests:
            sleep_time = self.per_seconds - (current_datetime - requests[0].datetime).total_seconds()
            if sleep_time > 0:
                logger.info('Throttling request by {} for {}'.format(sleep_time, self.model._meta.label))
                sleep(sleep_time)

            for _ in range(len(requests) - self.num_requests + 1):
                self.model.objects.order_by('datetime').first().delete()

        self.model.objects.create(datetime=current_datetime, **request_params)
