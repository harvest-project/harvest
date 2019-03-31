from django.db import OperationalError, transaction
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response

from Harvest.utils import TransactionAPIView
from upload_studio.models import Project
from upload_studio.serializers import ProjectShallowSerializer, ProjectDeepSerializer
from upload_studio.tasks import project_run_all, project_run_one


class ProjectsView(ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectShallowSerializer


class ProjectView(RetrieveDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDeepSerializer

    @transaction.atomic
    def perform_destroy(self, instance):
        instance = self.queryset.select_for_update().get(id=instance.id)
        instance.delete()


class ProjectMutatorView(TransactionAPIView):
    def perform_work(self, request, **kwargs):
        raise NotImplementedError()

    def post(self, request, pk, **kwargs):
        try:
            self.project = Project.objects.select_for_update(nowait=True).get(id=pk)
        except OperationalError:
            raise APIException(
                'Unable to perform action on project while it is running.',
                code=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_work(request, **kwargs)

        # Get a fresh copy for serialization
        self.project = Project.objects.get(id=pk)
        return Response(ProjectDeepSerializer(self.project).data)


class ProjectResetToStep(ProjectMutatorView):
    def perform_work(self, request, **kwargs):
        step_index = int(request.data['step'])
        self.project.reset(step_index)


class ProjectRunAll(ProjectMutatorView):
    def perform_work(self, request, **kwargs):
        project_run_all(self.kwargs['pk'])


class ProjectRunOne(ProjectMutatorView):
    def perform_work(self, request, **kwargs):
        project_run_one(self.kwargs['pk'])
