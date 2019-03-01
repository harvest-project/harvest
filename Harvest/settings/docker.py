from .production import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environ["POSTGRES_DB"],
        'USER': environ["POSTGRES_USER"],
        'PASSWORD': environ["POSTGRES_PASSWORD"],
        'HOST': 'db',
        'PORT': '5432',
    },
}
