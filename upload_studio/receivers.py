from upload_studio.models import Project
from upload_studio.tasks import project_run_all


def on_torrent_finished(sender, torrent, **kwargs):
    projects = Project.objects.filter(source_torrent=torrent, is_finished=False)
    for project in projects:
        project_run_all.delay(project.id)
