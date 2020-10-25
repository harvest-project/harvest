import os
import shutil
from io import BytesIO

from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from Harvest.path_utils import copytree_into
from Harvest.utils import get_logger
from monitoring.models import LogEntry
from upload_studio.models import ProjectStep, Project, ProjectStepWarning, ProjectStepError
from upload_studio.upload_metadata import MusicMetadata, MusicMetadataSerializer

logger = get_logger(__name__)


class StepAbortException(Exception):
    def __init__(self, status, *args, finish_project=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = status
        self.finish_project = finish_project


class StepExecutor:
    name = None
    description = None

    def __init__(self, project: Project, step: ProjectStep, prev_step: ProjectStep):
        self.project = project
        self.step = step
        self.prev_step = prev_step

        self.metadata = None
        if self.step.metadata_json:
            data = JSONParser().parse(BytesIO(self.step.metadata_json.encode()))
            serializer = MusicMetadataSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.metadata = MusicMetadata(**serializer.validated_data)

    @property
    def completed_status(self):
        return Project.STATUS_COMPLETE

    @transaction.atomic
    def add_warning(self, message, acked=False):
        try:
            ProjectStepWarning.objects.create(
                step=self.step,
                message=message,
                acked=acked,
            )
            logger.warning('Project {} step({}) {} added warning {}.',
                           self.project.id, self.step.id, self.name, message)
        except IntegrityError:
            logger.info('Project {} step({}) {} warning already added: {}.',
                        self.project.id, self.step.id, self.name, message)

    def raise_warnings(self):
        for warning in self.step.projectstepwarning_set.all():
            if not warning.acked:
                self.step.status = Project.STATUS_WARNINGS
                raise StepAbortException(Project.STATUS_WARNINGS)

    def raise_error(self, message, finish_project=False):
        logger.warning('Project {} step({}) {} raised error {}.',
                       self.project.id, self.step.id, self.name, message)
        ProjectStepError.objects.create(step=self.step, message=message)
        raise StepAbortException(
            Project.STATUS_ERRORS,
            finish_project=finish_project,
        )

    def clean_work_area(self):
        try:
            shutil.rmtree(self.step.path)
        except FileNotFoundError:
            pass
        os.makedirs(self.step.data_path)

    def copy_prev_step_area_files(self, area):
        copytree_into(self.prev_step.get_area_path(area), self.step.get_area_path(area))

    def copy_prev_step_files(self, exclude_areas=None):
        if not self.prev_step:
            self.raise_error('No previous step to copy files from.')
        exclude_areas = exclude_areas if exclude_areas is not None else {}
        for area in self.prev_step.get_areas():
            if area in exclude_areas:
                continue
            self.copy_prev_step_area_files(area)

    def handle_run(self):
        raise NotImplementedError()

    def run(self):
        self.step.projectsteperror_set.all().delete()
        try:
            self.clean_work_area()
            self.handle_run()
            self.raise_warnings()  # In case a warning was added after the last raise_warnings
            self.step.status = self.completed_status
        except StepAbortException as exc:
            self.step.status = exc.status
            if exc.finish_project:
                LogEntry.info('Finished upload studio {} due to error.'.format(self.project))
                self.project.finish()

        if self.metadata:
            data = MusicMetadataSerializer(self.metadata).data
            self.step.metadata_json = JSONRenderer().render(data).decode()
        self.step.save()
