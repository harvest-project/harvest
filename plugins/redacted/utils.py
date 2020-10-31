import html
import re
from dataclasses import dataclass

import bs4

from upload_studio.upload_metadata import MusicMetadata


class JoinedArtistsBuilder(object):
    def __init__(self, joined_artists_builder=None):
        if joined_artists_builder is None:
            self.result = []
        else:
            self.result = list(joined_artists_builder.result)

    def append_joined(self, join_string, artists):
        for a in artists:
            self.result.append({
                'id': a['id'],
                'name': a['name'],
                'join': join_string,
            })
        self.result[-1]['join'] = ''

    def append_artist(self, artist):
        self.result.append({
            'id': artist['id'],
            'name': html.unescape(artist['name']),
            'join': '',
        })

    def append_join(self, join_string):
        assert not self.result[-1]['join'], 'Last join should be empty before adding a new join'
        self.result[-1]['join'] = join_string

    def clear(self):
        self.result = []


def get_artists_list(music_info):
    a_main = music_info['artists']
    a_composers = music_info['composers']
    a_conductors = music_info['conductor']
    a_djs = music_info['dj']

    if len(a_main) == 0 and len(a_conductors) == 0 and len(a_djs) == 0 and len(a_composers) == 0:
        return []

    builder = JoinedArtistsBuilder()

    if len(a_composers) and len(a_composers) < 3:
        builder.append_joined(' & ', a_composers)
        if len(a_composers) < 3 and len(a_main) > 0:
            builder.append_join(' performed by ')

    composer_builder = JoinedArtistsBuilder(builder)

    if len(a_main):
        if len(a_main) <= 2:
            builder.append_joined(' & ', a_main)
        else:
            builder.append_artist({'id': -1, 'name': 'Various Artists'})

    if len(a_conductors):
        if (len(a_main) or len(a_composers)) and (len(a_composers) < 3 or len(a_main)):
            builder.append_join(' under ')
        if len(a_conductors) <= 2:
            builder.append_joined(' & ', a_conductors)
        else:
            builder.append_artist({'id': -1, 'name': 'Various Conductors'})

    if len(a_composers) and len(a_main) + len(a_conductors) > 3 and len(a_main) > 1 and len(
            a_conductors) > 1:
        builder = composer_builder
        builder.append_artist({'id': -1, 'name': 'Various Artists'})
    elif len(a_composers) > 2 and len(a_main) + len(a_conductors) == 0:
        builder.clear()
        builder.append_artist({'id': -1, 'name': 'Various Composers'})

    if len(a_djs):
        if len(a_djs) <= 2:
            builder.clear()
            builder.append_joined(' & ', a_djs)
        else:
            builder.clear()
            builder.append_artist({'id': -1, 'name': 'Various DJs'})

    return builder.result


def get_joined_artists(music_info):
    artists_list = get_artists_list(music_info)
    result = []
    for a in artists_list:
        result.append(a['name'])
        result.append(a['join'])
    return ''.join(result)


def get_shorter_joined_artists(music_info, group_name):
    artists = get_joined_artists(music_info)
    if len(artists) + len(group_name) > 80:
        if music_info['artists']:
            if len(music_info['artists']) > 1:
                artists = 'Various Artists'
            else:
                artists = music_info['artists'][0]['name']
        elif music_info['conductor']:
            if len(music_info['conductor']) > 1:
                artists = 'Various Conductors'
            else:
                artists = music_info['conductor'][0]['name']
    return artists


def extract_upload_errors(html):
    soup = bs4.BeautifulSoup(html, 'html5lib')
    return soup.find('p', attrs={'style': 'color: red; text-align: center;'}).text.strip()


_ENCODING_PREFERENCES = [
    MusicMetadata.ENCODING_320,
    MusicMetadata.ENCODING_V0,
    MusicMetadata.ENCODING_LOSSLESS,
    MusicMetadata.ENCODING_24BIT_LOSSLESS,
]


def select_best_torrents_from_torrent_dicts(torrents):
    def _is_torrent_better(a, b):
        try:
            a_index = _ENCODING_PREFERENCES.index(a['encoding'])
        except ValueError:
            a_index = -1
        try:
            b_index = _ENCODING_PREFERENCES.index(b['encoding'])
        except ValueError:
            b_index = -1
        if a_index > b_index:
            return True
        if a_index < b_index:
            return False
        return a['size'] > b['size']

    best_torrents = {}
    for torrent in torrents:
        key = (
            torrent['remasterYear'],
            torrent['remasterTitle'],
            torrent['remasterRecordLabel'],
            torrent['remasterCatalogueNumber'],
        )
        if not best_torrents.get(key) or _is_torrent_better(torrent, best_torrents[key]):
            best_torrents[key] = torrent
    return list(best_torrents.values())


@dataclass
class RedactedFileInfo:
    name: str
    size: int


def parse_file_list(file_list):
    items = file_list.split('|||')
    files = []
    for item in items:
        m = re.match('(.*){{{([0-9]*)}}}', item)
        files.append(RedactedFileInfo(m[1], int(m[2])))
    return files
