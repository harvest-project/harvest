from django.urls import path

from . import views

urlpatterns = [
    path('projects', views.Projects.as_view()),
    path('projects/<pk>', views.ProjectView.as_view()),
    path('projects/<pk>/reset-to-step', views.ProjectResetToStep.as_view()),
    path('projects/<pk>/run-all', views.ProjectRunAll.as_view()),
    path('projects/<pk>/run-one', views.ProjectRunOne.as_view()),
    path('projects/<pk>/finish', views.ProjectFinish.as_view()),
    path('projects/<pk>/insert-step', views.ProjectInsertStep.as_view()),
    path('projects/<pk>/warnings/<warning_id>/ack', views.WarningAck.as_view()),
    path('projects/<pk>/steps/<step_id>/executor-kwargs',
         views.ProjectStepExecutorKwargs.as_view()),
    path('projects/<pk>/steps/<step_id>/files', views.ProjectStepFiles.as_view()),
    path('projects/<pk>/steps/<step_id>/files/<area>/<filename>', views.project_step_file),
]
