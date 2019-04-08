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
    track = 1
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

    return track, disc


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


class InconsistentStreamInfoException(Exception):
    def __init__(self, stream_info_a, stream_info_b):
        super().__init__(
            'Different files have different audio stream configs. Detected both {} and {}. This is unsupported.'.format(
                stream_info_a, stream_info_b))


def get_stream_info(muta_objs):
    stream_info = None
    for muta in muta_objs:
        new_stream_info = StreamInfo(muta=muta)
        if stream_info is None:
            stream_info = new_stream_info
        if stream_info != new_stream_info:
            raise InconsistentStreamInfoException(stream_info, new_stream_info)
    return stream_info
