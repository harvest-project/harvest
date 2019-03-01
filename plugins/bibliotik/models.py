import pickle
from http import cookiejar

from django.db import models

from Harvest.throttling import ThrottledRequest


class BibliotikClientConfig(models.Model):
    username = models.TextField()
    password = models.TextField()
    is_server_side_login_enabled = models.BooleanField()

    # When the login was performed
    login_datetime = models.DateTimeField(null=True)
    # None if not logged in, set otherwise
    cookies = models.BinaryField(null=True)

    # Set if the last login attempt failed. Use to prevent login attempt flooding. Reset manually or by user/pass change
    last_login_failed = models.BooleanField(default=False)

    def clear_login_data(self):
        self.login_datetime = None
        self.cookies = None

    @property
    def cookie_jar(self):
        jar = cookiejar.CookieJar()
        if self.cookies:
            for cookie in pickle.loads(self.cookies):
                jar.set_cookie(cookie)
        return jar

    @cookie_jar.setter
    def cookie_jar(self, jar):
        self.cookies = pickle.dumps([c for c in jar])

    @classmethod
    def get_locked_config(cls):
        return cls.objects.select_for_update().get()

    @classmethod
    def get_config(cls):
        return cls.objects.get()


class BibliotikThrottledRequest(ThrottledRequest, models.Model):
    url = models.CharField(max_length=2048)  # Used for debugging purposes to watch what requests are going through
