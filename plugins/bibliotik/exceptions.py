from trackers.exceptions import TrackerException


class BibliotikException(TrackerException):
    pass


class BibliotikLoginException(BibliotikException):
    pass


class BibliotikBadTorrentIdException(BibliotikException):
    pass
