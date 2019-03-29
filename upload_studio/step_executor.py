import os
import shutil
from io import BytesIO

from psycopg2._psycopg import IntegrityError
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from upload_studio.models import ProjectStep, Project, ProjectStepWarning, ProjectStepError
from upload_studio.upload_metadata import MusicMetadata, MusicMetadataSerializer


class StepAbortException(Exception):
    pass


class StepExecutor:
    def __init__(self, project: Project, step: ProjectStep, prev_step: ProjectStep):
        self.project = project
        self.step = step
        self.prev_step = prev_step

        data = JSONParser().parse(BytesIO(self.step.metadata_json.encode()))
        self.metadata = MusicMetadata(**MusicMetadataSerializer(data=data).validated_data)

    @property
    def path(self):
        return os.path.join(self.project.data_path, 'step_{}'.format(self.step.id))

    @property
    def data_path(self):
        return os.path.join(self.path, 'data')

    def add_warning(self, message):
        try:
            ProjectStepWarning.objects.create(step=self.step, message=message)
        except IntegrityError:
            pass

    def raise_warnings(self):
        for warning in self.step.projectstepwarning_set.all():
            if not warning.acked:
                self.step.status = Project.STATUS_WARNINGS
                raise StepAbortException()

    def raise_error(self, message):
        ProjectStepError.objects.create(step=self.step, message=message)
        raise StepAbortException()

    def handle_run(self):
        raise NotImplementedError()

    def run(self):
        if os.path.exists(self.data_path):
            shutil.rmtree(self.data_path)

        self.step.projectsteperror_set.all().delete()
        try:
            self.handle_run()
        except StepAbortException:
            pass

        data = MusicMetadataSerializer(self.metadata).data
        self.step.metadata_json = JSONRenderer().render(data).decode()
        self.project.save_steps()
