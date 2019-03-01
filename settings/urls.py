from django.urls import path

from . import views

urlpatterns = [
    path('token', views.TokenView.as_view()),
]
