from django.urls import path

from . import views

urlpatterns = [
    path('projects', views.ProjectsView.as_view()),
    path('projects/<pk>', views.ProjectView.as_view()),
    path('projects/<pk>/reset-to-step', views.ProjectResetToStep.as_view()),
    path('projects/<pk>/run-all', views.ProjectRunAll.as_view()),
    path('projects/<pk>/run-one', views.ProjectRunOne.as_view()),
]
