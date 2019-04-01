from rest_framework import status
from rest_framework.exceptions import APIException


class ProjectFinishedException(APIException):
    default_detail = 'Unable to perform action on a finished project.'
    status_code = status.HTTP_400_BAD_REQUEST
