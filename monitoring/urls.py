from django.urls import path

from . import views

urlpatterns = [
    path('data', views.Data.as_view()),
]
