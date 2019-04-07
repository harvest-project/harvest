import json
import os
import shutil

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from rest_framework.exceptions import APIException

from torrents.models import Torrent
from upload_studio.exceptions import ProjectFinishedException


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

    created_datetime = models.DateTimeField(db_index=True, default=timezone.now)
    source_torrent = models.ForeignKey(Torrent, models.SET_NULL, null=True)
    name = models.CharField(max_length=1024)
    media_type = models.CharField(max_length=64, choices=MEDIA_TYPE_CHOICES)
    is_finished = models.BooleanField(db_index=True, default=False)
    finished_datetime = models.DateTimeField(null=True, db_index=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._steps = None

    def __str__(self):
        return 'Project(id={}, name={})'.format(self.id, self.name)

    @property
    def steps(self):
        if self._steps is None:
            self._steps = list(self.projectstep_set.order_by('index').all())
        return self._steps

    def raise_if_finished(self):
        if self.is_finished:
            raise ProjectFinishedException()

    @property
    def next_step(self):
        for step in self.steps:
            if step.status in {self.STATUS_PENDING, self.STATUS_WARNINGS, self.STATUS_ERRORS, self.STATUS_RUNNING}:
                return step
            elif step.status == self.STATUS_COMPLETE:
                continue
            elif step.status == self.STATUS_FINISHED:
                return None
        return None

    @property
    def last_complete_step(self):
        for step in reversed(self.steps):
            if step.status == self.STATUS_COMPLETE:
                return step
        return None

    def save_steps(self):
        for index, step in enumerate(self.steps):
            step.project = self
            step.index = index
            step.save()

    @property
    def status(self):
        if self.is_finished:
            return self.STATUS_FINISHED
        next_step = self.next_step
        if next_step:
            return next_step.status
        return self.STATUS_COMPLETE

    @property
    def data_path(self):
        return os.path.join(settings.MEDIA_ROOT, 'upload_project_{}'.format(self.id))

    def delete_all_data(self):
        try:
            shutil.rmtree(self.data_path)
        except FileNotFoundError:
            pass

    @transaction.atomic()
    def reset(self, step_index=0):
        for step in self.steps[:step_index]:
            if step.status != self.STATUS_COMPLETE:
                raise APIException('Unable to reset to a step, as previous steps are not completed.')
        self.raise_if_finished()
        for step in self.steps[step_index:]:
            step.reset()
        self.save_steps()
        if step_index == 0:
            self.delete_all_data()

    @transaction.atomic()
    def finish(self):
        shutil.rmtree(self.data_path)
        self.is_finished = True
        self.finished_datetime = timezone.now()
        self.save()


class ProjectStep(models.Model):
    project = models.ForeignKey(Project, models.CASCADE)
    index = models.IntegerField()
    status = models.CharField(max_length=64, choices=Project.STATUS_CHOICES, default=Project.STATUS_PENDING)
    executor_name = models.CharField(max_length=64)
    executor_kwargs_json = models.TextField(default='{}')
    metadata_json = models.TextField()

    @property
    def executor_kwargs(self):
        return json.loads(self.executor_kwargs_json)

    @executor_kwargs.setter
    def executor_kwargs(self, value):
        self.executor_kwargs_json = json.dumps(value)

    @property
    def description(self):
        from upload_studio.executor_registry import ExecutorRegistry
        kwargs = json.loads(self.executor_kwargs_json)
        kwargs['source_torrent'] = self.project.source_torrent
        return ExecutorRegistry.get_executor(self.executor_name).description.format(**kwargs)

    @property
    def path(self):
        return os.path.join(self.project.data_path, 'step_{}'.format(self.id))

    def get_area_path(self, area_name):
        return os.path.join(self.path, area_name)

    @property
    def data_path(self):
        return self.get_area_path('data')

    def reset(self):
        self.status = Project.STATUS_PENDING
        try:
            shutil.rmtree(self.path)
        except FileNotFoundError:
            pass
        self.projectstepwarning_set.all().delete()
        self.projectsteperror_set.all().delete()


class ProjectStepWarning(models.Model):
    step = models.ForeignKey(ProjectStep, models.CASCADE)
    message = models.TextField()
    acked = models.BooleanField(default=False)

    class Meta:
        ordering = ('message',)
        unique_together = (('step', 'message'),)


class ProjectStepError(models.Model):
    step = models.ForeignKey(ProjectStep, models.CASCADE)
    message = models.TextField()

    class Meta:
        ordering = ('message',)
