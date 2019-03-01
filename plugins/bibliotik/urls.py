from django.urls import path

from . import views

urlpatterns = [
    path('config', views.Config.as_view()),
    path('connection-test', views.ConnectionTest.as_view()),
    path('clear-login-data', views.ClearLoginData.as_view()),
    path('cookies', views.Cookies.as_view()),
]
