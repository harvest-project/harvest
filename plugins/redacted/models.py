from django.db import models

from Harvest.throttling import ThrottledRequest
from plugins.redacted.exceptions import RedactedException


class RedactedClientConfig(models.Model):
    username = models.TextField()
    password = models.TextField()

    login_datetime = models.DateTimeField(null=True)
    # None if not logged in, set otherwise
    cookies = models.BinaryField(null=True)
    authkey = models.TextField(null=True)
    passkey = models.TextField(null=True)

    # Set if the last login attempt failed. Use to prevent login attempt flooding. Reset manually or by user/pass change
    last_login_failed = models.BooleanField(default=False)

    def clear_login_data(self):
        self.login_datetime = None
        self.cookies = None
        self.authkey = None
        self.passkey = None

    @classmethod
    def get_locked_config(cls):
        return cls.objects.select_for_update().get()


class RedactedThrottledRequest(ThrottledRequest, models.Model):
    url = models.CharField(max_length=2048)  # Used for debugging purposes to watch what requests are going through
