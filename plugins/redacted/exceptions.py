from rest_framework import status

from trackers.exceptions import TrackerException, TorrentNotFoundException


class RedactedException(TrackerException):
    pass


class RedactedLoginException(RedactedException):
    pass


class RedactedTorrentNotFoundException(TorrentNotFoundException, RedactedException):
    pass


class RedactedArtistNotFoundException(TorrentNotFoundException, RedactedException):
    pass


class RedactedRateLimitExceededException(RedactedException):
    pass


class RedactedUploadException(RedactedException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, raw_response, parsed_error):
        self.raw_response = raw_response
        self.parsed_error = parsed_error
        super().__init__('Error uploading torrent to Redacted: {}'.format(parsed_error))
