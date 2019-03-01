from django.urls import path

from . import views

urlpatterns = [
    path('login', views.Login.as_view()),
    path('logout', views.Logout.as_view()),
    path('user', views.User.as_view()),
    path('ping', views.Ping.as_view()),
]
