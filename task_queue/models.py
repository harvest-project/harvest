import pickle

from django.db import models
# Create your models here.
from django.utils import timezone


class AsyncTask(models.Model):
    STATUS_PENDING = 0
    STATUS_EXECUTING = 1
    STATUS_SUCCEEDED = 2
    STATUS_ERRORED = 3
    STATUS_TIMED_OUT = 4
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_EXECUTING, 'Executing'),
        (STATUS_SUCCEEDED, 'Succeeded'),
        (STATUS_ERRORED, 'Errored'),
        (STATUS_TIMED_OUT, 'Timed Out'),
    )

    status = models.IntegerField(db_index=True, choices=STATUS_CHOICES, default=STATUS_PENDING)
    handler = models.CharField(max_length=128)
    args_pickle = models.BinaryField()
    created_datetime = models.DateTimeField(default=timezone.now)
    started_datetime = models.DateTimeField(null=True)
    completed_datetime = models.DateTimeField(null=True)
    traceback = models.TextField(null=True)

    @property
    def args(self):
        return pickle.loads(bytes(self.args_pickle))
