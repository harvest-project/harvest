from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import ComponentStatus, LogEntry
from monitoring.serializers import ComponentStatusSerializer, LogEntrySerializer


class ComponentStatuses(APIView):
    def get(self, request):
        return Response(ComponentStatusSerializer(
            ComponentStatus.objects.all().order_by('name'),
            many=True,
        ).data)


class LogEntries(APIView):
    def get(self, request):
        return Response(LogEntrySerializer(
            LogEntry.objects.all().order_by('-created_datetime')[:100],
            many=True,
        ).data)
