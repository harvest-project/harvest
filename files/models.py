import datetime
import os

import mutagen
import pytz

from files.audio_utils import stringify_tag, get_tag_value


class FileInfo:
    def __init__(self, abs_path, data_path):
        stat = os.stat(abs_path)
        self.abs_path = abs_path
        self.rel_path = os.path.relpath(abs_path, data_path)
        self.size = stat.st_size
        self.modified_datetime = datetime.datetime.utcfromtimestamp(
            stat.st_mtime).replace(tzinfo=pytz.utc).isoformat()


class AudioFileInfo:
    def __init__(self, abs_path, data_path):
        super().__init__(abs_path, data_path)

        muta = mutagen.File(abs_path, easy=True)
        self.artist = stringify_tag(get_tag_value(muta, 'artist', 'albumartist', 'performer'))
        self.album = stringify_tag(get_tag_value(muta, 'album'))
        self.title = stringify_tag(get_tag_value(muta, 'title'))
        self.duration = muta.info.length
