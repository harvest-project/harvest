from trackers.exceptions import TrackerException, TorrentNotFoundException


class BibliotikException(TrackerException):
    pass


class BibliotikLoginException(BibliotikException):
    pass


class BibliotikTorrentNotFoundException(TorrentNotFoundException):
    pass
