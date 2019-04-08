from task_queue.task_queue import TaskQueue
from upload_studio.steps_runner import StepsRunner


@TaskQueue.async_task()
def project_run_all(project_id):
    runner = StepsRunner(project_id)
    runner.run_all()


@TaskQueue.async_task()
def project_run_one(project_id):
    runner = StepsRunner(project_id)
    runner.run_one()
