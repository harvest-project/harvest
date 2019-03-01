from django.urls import path

from . import views

urlpatterns = [
    path('', views.Trackers.as_view()),
]
