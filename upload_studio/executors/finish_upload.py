import shutil

from upload_studio.models import Project
from upload_studio.step_executor import StepExecutor


class FinishUploadExecutor(StepExecutor):
    name = 'finish_upload'
    description = 'Finishes the upload, clears all working files.\nPrevents any further actions on the upload.'

    @property
    def completed_status(self):
        return Project.STATUS_FINISHED

    def handle_run(self):
        for step in self.project.steps:
            try:
                shutil.rmtree(step.path)
            except FileNotFoundError:
                pass
        self.project.is_finished = True
        self.project.save()
