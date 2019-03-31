import traceback

from django.db import transaction

from Harvest.utils import get_logger
from upload_studio.executor_registry import ExecutorRegistry
from upload_studio.models import Project, ProjectStepError

logger = get_logger(__name__)


class StepsRunner:
    def __init__(self, project_id):
        self.project_id = project_id
        self.project = None

    def get_prev_step(self, step):
        try:
            return self.project.steps[self.project.steps.index(step) - 1]
        except IndexError:
            return None

    def _run_one_guarded(self, step):
        logger.info('Project({}) {} running step({}) {} with kwargs {}.',
                    self.project.id, self.project.name, step.id, step.executor_name, step.executor_kwargs)

        step.status = Project.STATUS_RUNNING
        step.save(using='control', update_fields=('status',))
        with transaction.atomic():
            prev_step = self.get_prev_step(step)
            if prev_step:
                step.metadata_json = prev_step.metadata_json

            executor_class = ExecutorRegistry.get_executor(step.executor_name)
            executor = executor_class(
                project=self.project,
                step=step,
                prev_step=prev_step,
                **step.executor_kwargs,
            )
            executor.run()

    @transaction.atomic
    def run_one(self):
        self.project = Project.objects.select_for_update().get(id=self.project_id)
        self.project.raise_if_finished()
        step = self.project.next_step
        if step is None:
            return None
        try:
            self._run_one_guarded(step)
        except Exception as ex:
            logger.exception('Project({}) {} crashed running step({}) {} with kwargs {}.',
                             self.project.id, self.project.name, step.id, step.executor_name, step.executor_kwargs)
            with transaction.atomic():
                step.projectsteperror_set.all().delete()
                ProjectStepError.objects.create(
                    step=step,
                    message=traceback.format_exc(),
                )
                step.status = Project.STATUS_ERRORS
                step.save()
        self.project = None
        return step

    def run_all(self):
        while True:
            step = self.run_one()
            if step is None:
                logger.info('Project {} went through all steps.', self.project_id)
                break
            if step.status != Project.STATUS_COMPLETE:
                logger.info('Project {} stopping run all due to step({}) {} status {}.',
                            self.project.id, step.id, step.executor_name, step.status)
                break
