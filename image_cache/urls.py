from django.urls import path

from . import views

urlpatterns = [
    path('image', views.Image.as_view()),
]
