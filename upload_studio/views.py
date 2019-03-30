from rest_framework.generics import ListAPIView, RetrieveAPIView

from upload_studio.models import Project
from upload_studio.serializers import ProjectShallowSerializer, ProjectDeepSerializer


class ProjectsView(ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectShallowSerializer


class ProjectView(RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDeepSerializer
