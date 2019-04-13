import os

import mutagen

from Harvest.path_utils import list_rel_files
from Harvest.utils import get_logger
from files.audio_utils import StreamInfo, extract_track_disc_number, TrackDiscNumberExtractionException

logger = get_logger(__name__)


class InconsistentStreamInfoException(Exception):
    def __init__(self, stream_info_a, stream_info_b):
        super().__init__(
            'Different files have different audio stream configs. Detected both {} and {}. This is unsupported.'.format(
                stream_info_a, stream_info_b))


def get_stream_info(muta_objs):
    if not muta_objs:
        raise Exception('Unable to get stream info without input mutagen objects.')
    stream_info = None
    for muta in muta_objs:
        if muta is None:
            raise Exception('get_stream_info received a None muta object')
        new_stream_info = StreamInfo(muta=muta)
        if stream_info is None:
            stream_info = new_stream_info
        if stream_info != new_stream_info:
            raise InconsistentStreamInfoException(stream_info, new_stream_info)

    if not stream_info.sample_rate:
        raise Exception('get_stream_info ended up with bad sample rate {}'.format(stream_info.sample_rate))
    if not stream_info.channels:
        raise Exception('get_stream_info ended up with bad channels {}'.format(stream_info.channels))
    return stream_info


class AudioDiscoveryStepMixin:
    class FileInfo:
        def __init__(self, rel_path, abs_path):
            self.rel_path = rel_path
            self.abs_path = abs_path
            self.muta = mutagen.File(self.abs_path, easy=True)
            self.disc, self.track = extract_track_disc_number(self.muta)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_files = None
        self.stream_info = None

    def discover_audio_files(self):
        self.audio_files = []
        audio_ext = '.' + self.metadata.format.lower()
        for rel_path in list_rel_files(self.step.data_path):
            if not rel_path.lower().endswith(audio_ext):
                continue
            try:
                self.audio_files.append(self.FileInfo(
                    rel_path,
                    os.path.join(self.step.data_path, rel_path),
                ))
            except TrackDiscNumberExtractionException as exc:
                self.raise_error(str(exc))

        try:
            self.stream_info = get_stream_info(f.muta for f in self.audio_files)
        except InconsistentStreamInfoException as exc:
            self.raise_error(str(exc))

        failed_detecting = (
                not self.stream_info.sample_rate or
                not self.stream_info.channels or
                (not self.metadata.format_is_lossy and not self.stream_info.bits_per_sample)
        )
        if failed_detecting:
            self.raise_error('Failed detecting files stream info.')

        logger.info('{} detected stream settings {}.', self.project, self.stream_info)
