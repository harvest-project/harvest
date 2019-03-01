from trackers.exceptions import TrackerException


class RedactedException(TrackerException):
    pass


class RedactedLoginException(RedactedException):
    pass


class RedactedBadTorrentIdException(RedactedException):
    pass


class RedactedRateLimitExceededException(RedactedException):
    pass
