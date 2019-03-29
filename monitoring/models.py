import logging
import traceback

from django.db import models
from django.utils import timezone


class ComponentStatus(models.Model):
    STATUS_GREEN = 'green'
    STATUS_YELLOW = 'yellow'
    STATUS_RED = 'red'

    STATUS_CHOICES = (
        (STATUS_GREEN, STATUS_GREEN),
        (STATUS_YELLOW, STATUS_YELLOW),
        (STATUS_RED, STATUS_RED),
    )

    name = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=64, choices=STATUS_CHOICES)
    updated_datetime = models.DateTimeField()
    message = models.TextField()
    traceback = models.TextField(null=True)

    @classmethod
    def update_status(cls, name, status, message, traceback_str=None):
        cls.objects.using('control').update_or_create(
            name=name,
            defaults={
                'status': status,
                'updated_datetime': timezone.now(),
                'message': message,
                'traceback': traceback_str,
            }
        )


class LogEntry(models.Model):
    created_datetime = models.DateTimeField(db_index=True)
    level = models.IntegerField()
    message = models.TextField()
    traceback = models.TextField(null=True)

    @classmethod
    def log(cls, level, message, traceback_str=None):
        return cls.objects.using('control').create(
            created_datetime=timezone.now(),
            level=level,
            message=message,
            traceback=traceback_str,
        )

    @classmethod
    def critical(cls, message, traceback_str=None):
        return cls.log(logging.CRITICAL, message, traceback_str)

    @classmethod
    def error(cls, message, traceback_str=None):
        return cls.log(logging.ERROR, message, traceback_str)

    @classmethod
    def exception(cls, message):
        return cls.log(logging.ERROR, message, traceback.format_exc())

    @classmethod
    def warning(cls, message, traceback_str=None):
        return cls.log(logging.WARNING, message, traceback_str)

    @classmethod
    def info(cls, message, traceback_str=None):
        return cls.log(logging.INFO, message, traceback_str)

    @classmethod
    def debug(cls, message, traceback_str=None):
        return cls.log(logging.DEBUG, message, traceback_str)
