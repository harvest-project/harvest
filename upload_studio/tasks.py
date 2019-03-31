from huey.contrib.djhuey import db_task

from upload_studio.steps_runner import StepsRunner


@db_task()
def project_run_all(project_id):
    runner = StepsRunner(project_id)
    runner.run_all()


@db_task()
def project_run_one(project_id):
    runner = StepsRunner(project_id)
    runner.run_one()
