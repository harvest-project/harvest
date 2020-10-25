import html
from plugins.release_matching.models import ReleaseMatchInfo


class RedactedReleaseMatcher:
    def __init__(self, redacted_client):
        self.client = redacted_client

    def search(self, match_info):
        result = self.client.browse(
            search_string=match_info.normalized_artists_joined + ' ' + match_info.normalized_title,
            categories=(1,)
        )
        for group in result['results']:
            yield get_match_info_from_listing_group(group), group


def get_match_info_from_listing_group(group):
    return ReleaseMatchInfo(
        artists=tuple(html.unescape(a['name']) for a in group['torrents'][0]['artists']),
        title=html.unescape(group['groupName']),
    )
