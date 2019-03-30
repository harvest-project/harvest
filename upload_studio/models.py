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

    MEDIA_TYPE_MUSIC = 'music'
    MEDIA_TYPE_CHOICES = (
        (MEDIA_TYPE_MUSIC, MEDIA_TYPE_MUSIC),
    )

    name = models.CharField(max_length=1024)
    media_type = models.CharField(max_length=64, choices=MEDIA_TYPE_CHOICES)
    current_step = models.IntegerField(default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._steps = None

    @property
    def steps(self):
        if self._steps is None:
            self._steps = list(self.projectstep_set.order_by('index').all())
        return self._steps

    def save_steps(self):
        for index, step in enumerate(self.steps):
            step.project = self
            step.index = index
            step.save()

    @property
    def status(self):
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step].status
        return self.STATUS_COMPLETE

    @property
    def data_path(self):
        return os.path.join(settings.MEDIA, 'upload_project_{}'.format(self.id))


class ProjectStep(models.Model):
    project = models.ForeignKey(Project, models.CASCADE)
    index = models.IntegerField()
    status = models.CharField(max_length=64, choices=Project.STATUS_CHOICES, default=Project.STATUS_PENDING)
    executor_name = models.CharField(max_length=64)
    executor_kwargs_json = models.TextField()
    metadata_json = models.TextField()

    @property
    def path(self):
        return os.path.join(self.project.data_path, 'step_{}'.format(self.id))

    @property
    def data_path(self):
        return os.path.join(self.path, 'data')


class ProjectStepWarning(models.Model):
    step = models.ForeignKey(ProjectStep, models.CASCADE)
    message = models.TextField(unique=True)
    acked = models.BooleanField(default=False)


class ProjectStepError(models.Model):
    step = models.ForeignKey(ProjectStep, models.CASCADE)
    message = models.TextField()
