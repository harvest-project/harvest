from time import sleep

import coreapi
import coreschema
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView

from Harvest.utils import CORSBrowserExtensionView
from home.serializers import UserSerializer


class Index(TemplateView):
    template_name = 'index.html'


class Login(APIView):
    """Log in a user to Harvest."""

    schema = AutoSchema(manual_fields=[
        coreapi.Field('username', True, 'body', coreschema.String(description='Username of the user to log in.')),
        coreapi.Field('password', True, 'body', coreschema.String(description='Password of the user to log in.')),
    ])
    permission_classes = ()

    def post(self, request):
        if not request.user.is_anonymous:
            return Response({'detail': 'Already logged in.'}, status=400)

        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response(data=UserSerializer(user).data)
        else:
            return Response({'detail': 'Invalid username or password.'}, status=400)


class User(RetrieveAPIView):
    """Returns the currently authenticated user."""

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class Logout(APIView):
    """Log the current user out."""

    def post(self, request):
        logout(request)
        return Response({})


class Ping(CORSBrowserExtensionView, APIView):
    """Performs a ping to the API. Always returns `{"success": True}`. Used to check API connectivity and auth."""

    def get(self, request):
        return Response({
            'success': True,
        })
