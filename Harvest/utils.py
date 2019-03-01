import re

from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView


class TransactionAPIView(APIView):
    def dispatch(self, request, *args, **kwargs):
        with transaction.atomic():
            return super().dispatch(request, *args, **kwargs)


def get_filename_from_content_disposition(content_disposition):
    return re.search('filename="(.*)"', content_disposition).group(1)


class CORSBrowserExtensionView(APIView):
    def _should_pass_through(self, request):
        return (
                'HTTP_ORIGIN' in request.META and
                (
                        'chrome-extension://' in request.META['HTTP_ORIGIN'] or
                        'moz-extension://' in request.META['HTTP_ORIGIN']
                )
        )

    def check_permissions(self, request):
        if self.request.method == 'OPTIONS' and self._should_pass_through(request):
            return

        return super().check_permissions(request)

    def options(self, request, *args, **kwargs):
        return Response()

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self._should_pass_through(request):
            response['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']

            request_method = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD')
            if request_method:
                response['Access-Control-Allow-Methods'] = request_method

            request_headers = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
            if request_headers:
                response['Access-Control-Allow-Headers'] = request_headers

        return self.response
