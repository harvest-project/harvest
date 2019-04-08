import subprocess


def execute_subprocess_chain(chain):
    processes = []
    p_stdin = None

    for args in chain:
        p_stdout = None if args is chain[-1] else subprocess.PIPE
        p = subprocess.Popen(args, stdin=p_stdin, stdout=p_stdout)
        processes.append(p)
        p_stdin = p.stdout

    for p in reversed(processes):
        p.communicate()

    for p in processes:
        if p.returncode != 0:
            raise Exception('Subprocess returned non-zero.')


def pprint_subprocess_chain(chain):
    return ' | '.join(' '.join(args) for args in chain)


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
