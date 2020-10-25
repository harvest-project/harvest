import html

from plugins.release_matching.models import ReleaseMatchInfo


class RedactedReleaseMatcher:
    def __init__(self, redacted_client):
        self.client = redacted_client

    def search(self, match_info):
        search_parts = []
        if len(match_info.normalized_artists) <= 1:
            search_parts.append(match_info.normalized_artists_joined)
        search_parts.append(match_info.normalized_title)

        result = self.client.browse(
            search_string=' '.join(search_parts),
            categories=(1,)
        )
        for group in result['results']:
            yield get_match_info_from_listing_group(group), group


def get_match_info_from_listing_group(group):
    return ReleaseMatchInfo(
        artists=tuple(html.unescape(a['name']) for a in group['torrents'][0]['artists']),
        title=html.unescape(group['groupName']),
    )
