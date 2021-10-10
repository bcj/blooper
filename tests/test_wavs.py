import struct
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator


def test_record():
    from blooper.mixers import Mixer
    from blooper.wavs import BITS_PER_SAMPLE, SAMPLES_PER_SECOND, record

    class MockMixer(Mixer):
        def __init__(self, samples: list[list[float]]):
            self.samples = samples

        def mix(
            self, sample_rate: int, channels: int, max_value: int
        ) -> Generator[tuple[int, ...], None, None]:

            for sample_set in self.samples:
                assert len(sample_set) == channels

                yield tuple(round(channel * max_value) for channel in sample_set)

    with TemporaryDirectory() as directory_name:
        temp = Path(directory_name)

        # Honestly, it would be fine to break on empty files.
        # I'm sure other files do
        empty = temp / "empty.wav"
        record(empty, MockMixer([]))

        bytes_per_sample = BITS_PER_SAMPLE / 8
        block_align = 2 * bytes_per_sample
        byte_rate = SAMPLES_PER_SECOND * block_align

        assert empty.is_file()
        with empty.open("rb") as stream:
            # file header
            assert stream.read(4) == b"RIFF"
            assert struct.unpack("<I", stream.read(4)) == (36,)  # rest of file size
            assert stream.read(4) == b"WAVE"

            # format header
            assert stream.read(4) == b"fmt "
            assert struct.unpack("<I", stream.read(4)) == (16,)  # header size
            assert struct.unpack("<h", stream.read(2)) == (1,)  # no compression
            assert struct.unpack("<h", stream.read(2)) == (2,)  # channels
            assert struct.unpack("<I", stream.read(4)) == (SAMPLES_PER_SECOND,)
            assert struct.unpack("<I", stream.read(4)) == (byte_rate,)
            assert struct.unpack("<h", stream.read(2)) == (block_align,)
            assert struct.unpack("<h", stream.read(2)) == (BITS_PER_SAMPLE,)

            # data header
            assert stream.read(4) == b"data"
            assert struct.unpack("<I", stream.read(4)) == (0,)

        # declared size + 2 uncounted header values
        assert len(empty.read_bytes()) == 44

        # cursory check that options are being respected
        record(empty, MockMixer([]), channels=1, sample_rate=100, bits_per_sample=64)

        bytes_per_sample = 8
        block_align = bytes_per_sample
        byte_rate = 100 * block_align

        assert empty.is_file()
        with empty.open("rb") as stream:
            # file header
            assert stream.read(4) == b"RIFF"
            assert struct.unpack("<I", stream.read(4)) == (36,)  # rest of file size
            assert stream.read(4) == b"WAVE"

            # format header
            assert stream.read(4) == b"fmt "
            assert struct.unpack("<I", stream.read(4)) == (16,)  # header size
            assert struct.unpack("<h", stream.read(2)) == (1,)  # no compression
            assert struct.unpack("<h", stream.read(2)) == (1,)  # channels
            assert struct.unpack("<I", stream.read(4)) == (100,)
            assert struct.unpack("<I", stream.read(4)) == (byte_rate,)
            assert struct.unpack("<h", stream.read(2)) == (block_align,)
            assert struct.unpack("<h", stream.read(2)) == (64,)

            # data header
            assert stream.read(4) == b"data"
            assert struct.unpack("<I", stream.read(4)) == (0,)

        # declared size + 2 uncounted header values
        assert len(empty.read_bytes()) == 44

        # what if we actually try to write music
        mono = temp / "mono.wav"
        record(mono, MockMixer([[1], [-1], [0], [0.5]]), channels=1, bits_per_sample=64)

        bytes_per_sample = 8
        block_align = bytes_per_sample
        byte_rate = SAMPLES_PER_SECOND * block_align
        data_length = 4 * block_align

        assert mono.is_file()
        with mono.open("rb") as stream:
            # file header
            assert stream.read(4) == b"RIFF"
            assert struct.unpack("<I", stream.read(4)) == (36 + data_length,)
            assert stream.read(4) == b"WAVE"

            # format header
            assert stream.read(4) == b"fmt "
            assert struct.unpack("<I", stream.read(4)) == (16,)  # header size
            assert struct.unpack("<h", stream.read(2)) == (1,)  # no compression
            assert struct.unpack("<h", stream.read(2)) == (1,)  # channels
            assert struct.unpack("<I", stream.read(4)) == (SAMPLES_PER_SECOND,)
            assert struct.unpack("<I", stream.read(4)) == (byte_rate,)
            assert struct.unpack("<h", stream.read(2)) == (block_align,)
            assert struct.unpack("<h", stream.read(2)) == (64,)

            # data header
            assert stream.read(4) == b"data"
            assert struct.unpack("<I", stream.read(4)) == (data_length,)

            # data
            assert struct.unpack("<q", stream.read(8)) == ((2 ** 63) - 1,)
            assert struct.unpack("<q", stream.read(8)) == (-((2 ** 63) - 1),)
            assert struct.unpack("<q", stream.read(8)) == (0,)
            assert struct.unpack("<q", stream.read(8)) == (2 ** 62,)

        # declared size + 2 uncounted header values
        assert len(mono.read_bytes()) == 44 + data_length

        stereo = temp / "stereo.wav"
        record(stereo, MockMixer([[1, -1], [0, 0.5]]), channels=2, bits_per_sample=32)

        bytes_per_sample = 4
        block_align = 2 * bytes_per_sample
        byte_rate = SAMPLES_PER_SECOND * block_align
        data_length = 2 * block_align

        assert stereo.is_file()
        with stereo.open("rb") as stream:
            # file header
            assert stream.read(4) == b"RIFF"
            assert struct.unpack("<I", stream.read(4)) == (36 + data_length,)
            assert stream.read(4) == b"WAVE"

            # format header
            assert stream.read(4) == b"fmt "
            assert struct.unpack("<I", stream.read(4)) == (16,)  # header size
            assert struct.unpack("<h", stream.read(2)) == (1,)  # no compression
            assert struct.unpack("<h", stream.read(2)) == (2,)  # channels
            assert struct.unpack("<I", stream.read(4)) == (SAMPLES_PER_SECOND,)
            assert struct.unpack("<I", stream.read(4)) == (byte_rate,)
            assert struct.unpack("<h", stream.read(2)) == (block_align,)
            assert struct.unpack("<h", stream.read(2)) == (32,)

            # data header
            assert stream.read(4) == b"data"
            assert struct.unpack("<I", stream.read(4)) == (data_length,)

            # data
            assert struct.unpack("<i", stream.read(4)) == ((2 ** 31) - 1,)
            assert struct.unpack("<i", stream.read(4)) == (-((2 ** 31) - 1),)
            assert struct.unpack("<i", stream.read(4)) == (0,)
            assert struct.unpack("<i", stream.read(4)) == (2 ** 30,)

        # declared size + 2 uncounted header values
        assert len(stereo.read_bytes()) == 44 + data_length
