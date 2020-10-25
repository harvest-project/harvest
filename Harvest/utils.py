import inspect
import logging
import re
from contextlib import contextmanager

from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView


class TransactionAPIView(APIView):
    def dispatch(self, request, *args, **kwargs):
        with transaction.atomic():
            return super().dispatch(request, *args, **kwargs)


def union_dicts(*dicts):
    return dict(item for d in dicts for item in d.items())


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


def chunks(iterable, n):
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= n:
            yield chunk
            chunk = []
    if len(chunk):
        yield chunk


def qs_chunks(qs, n):
    ids = list(qs.values_list('id', flat=True))
    for ids_chunk in chunks(ids, n):
        yield qs.model.objects.filter(pk__in=ids_chunk)


@contextmanager
def control_transaction():
    exc = None
    with transaction.atomic(using='control'):
        try:
            yield
        except Exception as e:
            exc = e
    if exc is not None:
        raise exc


class BraceMessage(object):
    def __init__(self, fmt, args, kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return str(self.fmt).format(*self.args, **self.kwargs)


class BraceAdapter(logging.LoggerAdapter):
    def __init__(self, logger):
        super().__init__(logger, None)

    def log(self, level, msg, *args, **kwargs):
        if self.isEnabledFor(level):
            msg, log_kwargs = self.process(msg, kwargs)
            self.logger._log(
                level,
                BraceMessage(msg, args, kwargs),
                (),
                **log_kwargs,
            )

    def process(self, msg, kwargs):
        return msg, {key: kwargs[key]
                     for key in inspect.getfullargspec(self.logger._log).args[1:]
                     if key in kwargs}


def get_logger(name):
    return BraceAdapter(logging.getLogger(name))


def seconds_display(total_seconds):
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return '{}:{:02d}'.format(minutes, seconds)
