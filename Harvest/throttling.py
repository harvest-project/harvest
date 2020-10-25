from datetime import timedelta
from time import sleep

from django.db import models
from django.utils import timezone

from Harvest.utils import control_transaction, get_logger

logger = get_logger(__name__)


class ThrottledRequest(models.Model):
    datetime = models.DateTimeField()

    class Meta:
        abstract = True


class DatabaseSyncedThrottler:
    def __init__(self, config_model, model, num_requests, per_seconds):
        self.config_model = config_model
        self.model = model
        self.num_requests = num_requests
        self.per_seconds = per_seconds

    def _prune(self):
        self.model.objects.using('control').filter(
            datetime__lt=timezone.now() - timedelta(seconds=self.per_seconds)).delete()

    @control_transaction()
    def throttle_request(self, **request_params):
        list(self.config_model.objects.using('control').select_for_update().all())
        self._prune()
        requests = list(self.model.objects.using('control').order_by('datetime'))
        if len(requests) >= self.num_requests:
            sleep_time = self.per_seconds - (timezone.now() - requests[0].datetime).total_seconds()
            if sleep_time > 0:
                logger.info('Throttling request by {} for {}', sleep_time, self.model._meta.label)
                sleep(sleep_time)
        self.model.objects.using('control').create(datetime=timezone.now(), **request_params)

    @control_transaction()
    def get_load(self):
        list(self.config_model.objects.using('control').select_for_update().all())
        self._prune()
        return self.model.objects.using('control').order_by('datetime').count() / self.num_requests
