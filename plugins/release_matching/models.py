import re

from unidecode import unidecode

RELEASE_SUFFIXES_TO_REMOVE = {
    ' ep',
    ' e.p.',
    ' (ep)',
    ' (e.p.)',
}

EDITION_KEYWORDS = {
    'deluxe', 'remaster', 'score', 'music', 'anniversary', 'edition', 'soundtrack', 'live',
    'explicit', 'reissue', 'instrumental', 'bonus',
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
    # Remove known bad suffixes
    for suffix in RELEASE_SUFFIXES_TO_REMOVE:
        if title.endswith(suffix):
            title = title[:-len(suffix)].strip()
    # Replace slashes with spaces
    title = title.replace('/', ' ')
    # Remove things like (Remastered Edition), (Original Soundtrack) and so on
    title = re.sub(
        r'\([^()]*(' +
        '|'.join(EDITION_KEYWORDS) +
        r')[^()]*\)',
        '',
        title,
    )
    # Remove things like ": Remastered Edition" or " - Remastered Edition"
    title = re.sub(
        r':[^:]*(' +
        '|'.join(EDITION_KEYWORDS) +
        r')[^:]*^',
        '',
        title,
    )
    title = re.sub(
        r'-[^-]*(' +
        '|'.join(EDITION_KEYWORDS) +
        r')[^-]*^',
        '',
        title,
    )
    # Remove common non-alphanumeric characters
    title = re.sub(r'[-:(),"]', '', title)
    # Remove consecutive spaces
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
