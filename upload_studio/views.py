from django.db import OperationalError, transaction
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import RetrieveDestroyAPIView, GenericAPIView
from rest_framework.response import Response

from Harvest.utils import TransactionAPIView, CORSBrowserExtensionView
from monitoring.models import LogEntry
from upload_studio.models import Project, ProjectStepWarning
from upload_studio.serializers import ProjectShallowSerializer, ProjectDeepSerializer
from upload_studio.tasks import project_run_all, project_run_one


class Projects(CORSBrowserExtensionView, GenericAPIView):
    queryset = Project.objects.all()

    def filter_queryset(self, queryset):
        source_tracker_id = self.request.query_params.get('source_tracker_id')
        if source_tracker_id:
            queryset = queryset.filter(source_torrent__torrent_info__tracker_id=source_tracker_id)
        return queryset

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        active_qs = queryset.filter(is_finished=False).order_by('-created_datetime')
        history_qs = queryset.filter(is_finished=True).order_by('-finished_datetime')[:50]
        return Response({
            'active': ProjectShallowSerializer(active_qs, many=True).data,
            'history': ProjectShallowSerializer(history_qs, many=True).data,
        })


class ProjectView(RetrieveDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDeepSerializer

    @transaction.atomic
    def perform_destroy(self, instance):
        instance = self.queryset.select_for_update().get(id=instance.id)
        instance.delete_all_data()
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
        project_run_all.delay(self.project.id)


class ProjectRunOne(ProjectMutatorView):
    def perform_work(self, request, **kwargs):
        project_run_one.delay(self.project.id)


class ProjectFinish(ProjectMutatorView):
    def perform_work(self, request, **kwargs):
        LogEntry.info('Manually finished upload studio {}.'.format(self.project))
        self.project.finish()


class WarningAck(ProjectMutatorView):
    def perform_work(self, request, **kwargs):
        try:
            warning = ProjectStepWarning.objects.get(step__project=self.project, id=kwargs['warning_id'])
        except ProjectStepWarning.DoesNotExist:
            raise APIException('Warning does not exist.', code=status.HTTP_404_NOT_FOUND)
        if warning.acked:
            raise APIException('Warning already acked.', code=status.HTTP_400_BAD_REQUEST)
        warning.acked = True
        warning.save()
        step = self.project.next_step
        if step and not step.projectstepwarning_set.filter(acked=False).exists():
            project_run_all.delay(self.project.id)
