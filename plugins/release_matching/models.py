import re

from unidecode import unidecode

RELEASE_IDENTIFIERS = {
    'deluxe',
    'remastered',
    'deluxe edition',
    'edición remasterizada',
    'radio edit',
}


def _normalize_artist(artist):
    artist = artist.lower()
    artist = artist.replace('/', ' ').replace('-', ' ')
    # Remove anything parentheses
    artist = re.sub(
        r'\(.*\)',
        '',
        artist,
    )
    artist = re.sub(' +', ' ', artist)
    artist = artist.strip()
    return artist


def _normalize_title(title):
    title = title.lower()
    for release_identifier in RELEASE_IDENTIFIERS:
        title = title.replace('({})'.format(release_identifier), '')
    title = title.replace('/', ' ').replace('-', ' ')
    # Remove things like (Remastered Edition), (Original Soundtrack) and so on
    title = re.sub(
        r'\([^()]*(' +
        '|'.join((
            'deluxe', 'remaster', 'score', 'music', 'anniversary', 'edition', 'soundtrack', 'live',
            'explicit', 'reissue', 'instrumental',
        )) +
        r')[^()]*\)',

        '',
        title,
    )
    title = re.sub(' +', ' ', title)
    title = title.strip()
    return title


class ReleaseMatchInfo:
    def __init__(self, artists, title):
        self.artists = artists
        self.title = title

        self.joined_artists = ', '.join(self.artists)
        self.normalized_artists = [_normalize_artist(artist) for artist in artists]
        self.normalized_artists_joined = ' '.join(self.normalized_artists)
        self.normalized_title = _normalize_title(self.title)

    def equals(self, match_info):
        if unidecode(self.normalized_title) != unidecode(match_info.normalized_title):
            return False

        decoded_artists = {unidecode(a) for a in self.normalized_artists}
        match_info_decoded_artists = {unidecode(a) for a in match_info.normalized_artists}
        if len(decoded_artists & match_info_decoded_artists) == 0:
            return False

        return True

    def __str__(self):
        return 'MatchInfo({} - {})'.format(self.joined_artists, self.title)
