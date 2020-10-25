from django.urls import path

from . import views

urlpatterns = [
    path('component-statuses', views.ComponentStatuses.as_view()),
    path('log-entries', views.LogEntries.as_view()),
]
