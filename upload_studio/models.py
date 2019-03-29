import os

from django.conf import settings
from django.db import models


class Project(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_WARNINGS = 'warnings'
    STATUS_ERRORS = 'errors'
    STATUS_COMPLETE = 'complete'
    STATUS_FINISHED = 'finished'
    STATUS_CHOICES = (
        (STATUS_PENDING, STATUS_PENDING),
        (STATUS_RUNNING, STATUS_RUNNING),
        (STATUS_WARNINGS, STATUS_WARNINGS),
        (STATUS_ERRORS, STATUS_ERRORS),
        (STATUS_COMPLETE, STATUS_COMPLETE),
        (STATUS_FINISHED, STATUS_FINISHED),
    )

    MEDIA_MUSIC = 'music'
    MEDIA_TYPE_CHOICES = (
        (MEDIA_MUSIC, MEDIA_MUSIC),
    )

    name = models.CharField(max_length=1024)
    media_type = models.CharField(max_length=64, choices=MEDIA_TYPE_CHOICES)
    current_step = models.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._steps = None

    @property
    def steps(self):
        if self._steps is None:
            self._steps = list(self.projectstep_set.order_by('index').all())
        return self._steps

    def save_steps(self):
        for index, step in self.steps:
            step.index = index
            step.save()

    @property
    def status(self):
        return self.steps[self.current_step].status

    @property
    def data_path(self):
        return os.path.join(settings.MEDIA, 'upload_project_{}'.format(self.id))


class ProjectStep(models.Model):
    project = models.ForeignKey(Project, models.CASCADE)
    index = models.IntegerField()
    status = models.CharField(max_length=64)
    executor_name = models.CharField(max_length=64)
    executor_kwargs_json = models.TextField()
    metadata_json = models.TextField()


class ProjectStepWarning(models.Model):
    step = models.ForeignKey(ProjectStep, models.CASCADE)
    message = models.TextField(unique=True)
    acked = models.BooleanField(default=False)


class ProjectStepError(models.Model):
    step = models.ForeignKey(ProjectStep, models.CASCADE)
    message = models.TextField()
