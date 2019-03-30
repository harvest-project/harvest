from django.urls import path

from . import views

urlpatterns = [
    path('projects', views.ProjectsView.as_view()),
    path('projects/<pk>', views.ProjectView.as_view()),
]
