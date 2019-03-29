from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import ComponentStatus, LogEntry
from monitoring.serializers import ComponentStatusSerializer, LogEntrySerializer


class Data(APIView):
    def get(self, request):
        component_statuses = ComponentStatus.objects.all().order_by('name')
        log_entries = LogEntry.objects.all().order_by('-created_datetime')[:100]

        return Response({
            'component_statuses': ComponentStatusSerializer(component_statuses, many=True).data,
            'log_entries': LogEntrySerializer(log_entries, many=True).data,
        })
