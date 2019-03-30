import os
import shutil
from io import BytesIO

from psycopg2._psycopg import IntegrityError
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from Harvest.utils import get_logger
from upload_studio.models import ProjectStep, Project, ProjectStepWarning, ProjectStepError
from upload_studio.upload_metadata import MusicMetadata, MusicMetadataSerializer
from upload_studio.utils import copytree_into

logger = get_logger(__name__)


class StepAbortException(Exception):
    def __init__(self, status, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = status


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

    def add_warning(self, message):
        try:
            ProjectStepWarning.objects.create(step=self.step, message=message)
            logger.warning('Project {} step({}) {} added warning {}.',
                           self.project.id, self.step.id, self.name, message)
        except IntegrityError:
            logger.info('Project {} step({}) {} warning already acked: {}.',
                        self.project.id, self.step.id, self.name, message)

    def raise_warnings(self):
        for warning in self.step.projectstepwarning_set.all():
            if not warning.acked:
                self.step.status = Project.STATUS_WARNINGS
                raise StepAbortException(Project.STATUS_WARNINGS)

    def raise_error(self, message):
        logger.warning('Project {} step({}) {} raised error {}.',
                       self.project.id, self.step.id, self.name, message)
        ProjectStepError.objects.create(step=self.step, message=message)
        raise StepAbortException(Project.STATUS_ERRORS)

    def clean_work_area(self):
        if os.path.exists(self.step.data_path):
            shutil.rmtree(self.step.data_path)
        os.makedirs(self.step.data_path)

    def copy_prev_step_files(self):
        copytree_into(self.prev_step.data_path, self.step.data_path)

    def handle_run(self):
        raise NotImplementedError()

    def run(self):
        self.step.projectsteperror_set.all().delete()
        try:
            self.handle_run()
            self.raise_warnings()  # In case a warning was added after the last raise_warnings
            self.step.status = self.completed_status
        except StepAbortException as exc:
            self.step.status = exc.status

        if self.metadata:
            data = MusicMetadataSerializer(self.metadata).data
            self.step.metadata_json = JSONRenderer().render(data).decode()
        self.step.save()
