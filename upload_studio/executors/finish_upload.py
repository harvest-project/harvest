import shutil

from monitoring.models import LogEntry
from upload_studio.models import Project
from upload_studio.step_executor import StepExecutor


class FinishUploadExecutor(StepExecutor):
    name = 'finish_upload'
    description = 'Finishes the upload, clears all working files.\nPrevents any further actions on the upload.'

    @property
    def completed_status(self):
        return Project.STATUS_FINISHED

    def handle_run(self):
        shutil.rmtree(self.project.data_path)
        self.project.is_finished = True
        self.project.save()
        LogEntry.info('Finished upload studio {}.'.format(self.project))
