import base64
import hashlib
import mimetypes
import os
from itertools import count
from time import time

import requests
from django.conf import settings
from django.http import HttpResponse
from requests import RequestException
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

FAILURE_TTL = 24 * 3600
RETRIES = 3
CACHE_CONTROL = 'public, max-age=86400'


class Image(APIView):
    def _fetch(self, url):
        for i in count(1):
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response.content
            except RequestException:
                if i >= RETRIES:
                    raise

    def get(self, request):
        url = request.GET['url']
        dir_name = hashlib.md5(url.encode()).hexdigest()[:2]
        dir_path = os.path.join(settings.MEDIA_ROOT, 'image_cache', dir_name)
        path = os.path.join(
            dir_path,
            base64.b64encode(url.encode()).decode() + os.path.splitext(url)[1],
        )

        if os.path.exists(path):
            return HttpResponse(open(path, 'rb'), content_type=mimetypes.guess_type(path)[0])

        path_fail = path + '.fail'
        if os.path.exists(path_fail):
            fail_mtime = os.path.getmtime(path_fail)
            if time() - fail_mtime < FAILURE_TTL:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            content = self._fetch(url)
        except RequestException:
            os.makedirs(dir_path, exist_ok=True)
            with open(path_fail, 'wb'):
                pass
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            os.remove(path_fail)
        except FileNotFoundError:
            pass

        os.makedirs(dir_path, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(content)
        return HttpResponse(open(path, 'rb'), content_type=mimetypes.guess_type(path)[0])
