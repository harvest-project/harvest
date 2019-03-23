from trackers.exceptions import TrackerException, TorrentNotFoundException


class RedactedException(TrackerException):
    pass


class RedactedLoginException(RedactedException):
    pass


class RedactedTorrentNotFoundException(TorrentNotFoundException, RedactedException):
    pass


class RedactedRateLimitExceededException(RedactedException):
    pass
