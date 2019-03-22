from django.db import models


class InfoHashField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 40)
        super().__init__(*args, **kwargs)
