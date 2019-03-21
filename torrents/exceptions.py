from rest_framework.exceptions import APIException


class AlcazarNotConfiguredException(Exception):
    pass


class RealmNotFoundException(APIException):
    status_code = 400

    def __init__(self, realm_name):
        super('Realm {} not found. Please create one by adding an instance.'.format(realm_name))
