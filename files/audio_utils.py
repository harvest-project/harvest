from Harvest.utils import get_logger

logger = get_logger(__name__)


def stringify_tag(value):
    if value is None:
        return None
    elif isinstance(value, list):
        return ', '.join(str(i) for i in value)
    elif isinstance(value, int):
        return str(value)
    elif not isinstance(value, str):
        return value
    raise Exception('Unknown tag value type {}'.format(type(value).__name__))


def get_tag_value(tags, *keys):
    for key in keys:
        value = tags.get(key)
        if value:
            return value
    return None


class StreamInfo:
    def __init__(self, *, sample_rate=None, bits_per_sample=None, channels=None, muta=None):
        if muta:
            self.sample_rate = muta.info.sample_rate
            self.bits_per_sample = getattr(muta.info, 'bits_per_sample', None)
            self.channels = muta.info.channels
        else:
            self.sample_rate = sample_rate
            self.bits_per_sample = bits_per_sample
            self.channels = channels

    def __str__(self):
        return '{}/{}/{}'.format(self.sample_rate, self.bits_per_sample or 'no bit depth', self.channels)

    def __eq__(self, other):
        return (
                self.sample_rate == other.sample_rate and
                self.bits_per_sample == other.bits_per_sample and
                self.channels == other.channels
        )

    def __hash__(self):
        return hash((self.sample_rate, self.bits_per_sample, self.channels))

    def __lt__(self, other):
        return (
                (self.sample_rate, self.bits_per_sample, self.channels) <
                (other.sample_rate, other.bits_per_sample, other.channels)
        )


class TrackDiscNumberExtractionException(Exception):
    pass


def _try_parse(value):
    try:
        return int(value)
    except ValueError:
        return value


def _extract_number_from_tag_value(value):
    if isinstance(value, list):
        value = value[0]
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        raise TrackDiscNumberExtractionException('Expected final type str, got another.')
    return _try_parse(value.split('/')[0])


def extract_track_disc_number(tags):
    disc = 1

    disc_src = tags.get('discnumber') or tags.get('disc')
    if disc_src is not None:
        try:
            disc = _extract_number_from_tag_value(disc_src)
        except ValueError:
            raise TrackDiscNumberExtractionException('Unable to read disc_src {}.'.format(disc_src))

    track_src = tags.get('tracknumber') or tags.get('track')
    if track_src is None:
        raise TrackDiscNumberExtractionException('Missing track tag.')
    else:
        try:
            track = _extract_number_from_tag_value(track_src)
        except ValueError:
            raise TrackDiscNumberExtractionException('Unable read track_src {}.'.format(track_src))

    return disc, track
