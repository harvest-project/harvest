from rest_framework.response import Response
from rest_framework.views import APIView

from trackers.registry import TrackerRegistry
from trackers.serializers import TrackerSerializer


class Trackers(APIView):
    def get(self, request):
        trackers = TrackerRegistry.get_plugins()
        return Response({
            'trackers': TrackerSerializer(trackers, many=True).data,
        })
