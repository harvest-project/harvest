from Harvest.utils import get_logger

logger = get_logger(__name__)


def stringify_tag(value):
    if value is None:
        return None
    elif isinstance(value, list):
        return ', '.join(str(i) for i in value)
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, str):
        return value
    raise Exception('Unknown tag value type {}'.format(type(value).__name__))


class StreamInfo:
    def __init__(self, *, sample_rate=None, bits_per_sample=None, channels=None, muta=None):
        if muta is None:
            self.sample_rate = sample_rate
            self.bits_per_sample = bits_per_sample
            self.channels = channels
        else:
            self.sample_rate = muta.info.sample_rate
            self.bits_per_sample = getattr(muta.info, 'bits_per_sample', None)
            self.channels = muta.info.channels

            if not self.sample_rate:
                raise Exception(
                    'Got bad sample rate of {} for {}'.format(self.sample_rate, muta.filename))
            if not self.channels:
                raise Exception(
                    'Got bad channels of {} for {}'.format(self.channels, muta.filename))

    def __str__(self):
        return '{}/{}/{}'.format(self.sample_rate, self.bits_per_sample or 'no bit depth',
                                 self.channels)

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


def extract_disc_track_number(muta):
    disc = 0
    disc_src = muta.get('discnumber') or muta.get('disc')

    if disc_src is not None:
        try:
            disc = _extract_number_from_tag_value(disc_src)
        except ValueError:
            raise TrackDiscNumberExtractionException('Unable to read disc_src {} from {}'.format(
                disc_src, muta.filename))

    track = 0
    track_src = muta.get('tracknumber') or muta.get('track')

    if track_src is None:
        # Avoid errors for super short files (< 5 seconds), e.g. HTOA
        if muta.info.length >= 5:
            raise TrackDiscNumberExtractionException(
                'Missing track tag from {}'.format(muta.filename))
    else:
        try:
            track = _extract_number_from_tag_value(track_src)
        except ValueError:
            raise TrackDiscNumberExtractionException('Unable read track_src {} from {}'.format(
                track_src, muta.filename))

    return disc, track
