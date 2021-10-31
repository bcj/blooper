import struct
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator, Iterable

import pytest


def round_samples(
    samples: Iterable[tuple[float, ...]], precision: int = 8
) -> list[tuple[float, ...]]:
    return [
        tuple(round(channel, precision) for channel in sample) for sample in samples
    ]


class MockMixer:
    def __init__(self, samples: list[list[float]]):
        self.samples = samples

    def mix(
        self, sample_rate: int, channels: int, max_value: int
    ) -> Generator[tuple[int, ...], None, None]:

        for sample_set in self.samples:
            assert len(sample_set) == channels

            yield tuple(round(channel * max_value) for channel in sample_set)


def test_record():
    from blooper.wavs import BITS_PER_SAMPLE, SAMPLES_PER_SECOND, record

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


def test_wav_sample():
    from blooper.wavs import WavSample, record

    with TemporaryDirectory() as directory_name:
        temp = Path(directory_name)

        path = temp / "sample.wav"

        record(
            path,
            MockMixer([[1], [-1], [0], [0.5]]),
            channels=1,
            sample_rate=1000,
            bits_per_sample=64,
        )

        sample = WavSample.from_path(path)
        assert sample.channels == 1
        assert sample.sample_rate == 1000
        assert sample == WavSample.from_path(path)
        assert sample != WavSample.from_path(Path("./"))
        assert sample != path

        assert repr(sample) == f"WavSample({path!r})"

        # matching sample rate
        assert list(sample.load(1000, [1, 1, 1, 1])) == [(1,), (-1,), (0,), (0.5,)]

        # shorter
        assert list(sample.load(1000, [2, 0.75, 0])) == [(2,), (-0.75,), (0,)]

        # longer
        assert list(sample.load(1000, [1, 1, 1, 1, 0.5, 0.5])) == [
            (1,),
            (-1,),
            (0,),
            (0.5,),
        ]

        # longer (loop)
        assert list(sample.load(1000, [1, 1, 1, 1, 0.5, 0.5], loop=True)) == [
            (1,),
            (-1,),
            (0,),
            (0.5,),
            (0.5,),
            (-0.5,),
        ]

        # half sample-rate
        record(
            path,
            MockMixer([[1, 1], [0.8, 0.6], [0, 0], [-0.2, -1], [-1, -1], [-0.6, 0.2]]),
            channels=2,
            sample_rate=100,
            bits_per_sample=32,
        )
        sample = WavSample.from_path(path)
        assert sample.sample_rate == 100
        assert sample.channels == 2

        assert round_samples(sample.load(50, [1, 1, 1, 1], loop=False)) == [
            (0.9, 0.8),
            (-0.1, -0.5),
            (-0.8, -0.4),
        ]

        # partial sample reads
        assert round_samples(sample.load(20, [1, 1], loop=False)) == [
            (0.12, -0.08),
            (-0.6, 0.2),
        ]

        # loop across sample reads
        assert round_samples(sample.load(20, [1, 1], loop=True)) == [
            (0.12, -0.08),
            (0.2, 0.16),
        ]

        # invalid sample rate
        with pytest.raises(ValueError):
            print(round_samples(sample.load(200, [1, 1], loop=True)))

        # Some invalid files (love to test for coverage)
        with pytest.raises(ValueError):
            WavSample.from_path(Path(__file__)).channels

        # RIFF wrong
        invalid = temp / "invalid.wav"
        with invalid.open("wb") as stream:
            stream.write(b"RAFF")
            stream.write(struct.pack("<I", 36))
            stream.write(b"WAVE")

        with pytest.raises(ValueError):
            WavSample.from_path(invalid).channels

        # WAVE wrong
        with invalid.open("wb") as stream:
            stream.write(b"RIFF")
            stream.write(struct.pack("<I", 36))
            stream.write(b"SAVE")

        with pytest.raises(ValueError):
            WavSample.from_path(invalid).channels

        # fmt wrong
        with invalid.open("wb") as stream:
            stream.write(b"RIFF")
            stream.write(struct.pack("<I", 36))
            stream.write(b"WAVE")

            stream.write(b"frmt")
            stream.write(struct.pack("<IhhIIhh", 16, 1, 1, 1000, 4000, 4, 32))

        with pytest.raises(ValueError):
            WavSample.from_path(invalid).channels

        # only support PCM format
        with invalid.open("wb") as stream:
            stream.write(b"RIFF")
            stream.write(struct.pack("<I", 36))
            stream.write(b"WAVE")

            stream.write(b"fmt ")
            stream.write(struct.pack("<IhhIIhh", 18, 1, 1, 1000, 4000, 4, 32))

        with pytest.raises(NotImplementedError):
            WavSample.from_path(invalid).channels

        with invalid.open("wb") as stream:
            stream.write(b"RIFF")
            stream.write(struct.pack("<I", 36))
            stream.write(b"WAVE")

            stream.write(b"fmt ")
            stream.write(struct.pack("<IhhIIhh", 16, 2, 1, 1000, 4000, 4, 32))

        with pytest.raises(NotImplementedError):
            WavSample.from_path(invalid).channels

        # header math is wrong
        with invalid.open("wb") as stream:
            stream.write(b"RIFF")
            stream.write(struct.pack("<I", 36))
            stream.write(b"WAVE")

            stream.write(b"fmt ")
            stream.write(struct.pack("<IhhIIhh", 16, 1, 1, 1000, 5000, 4, 32))

        with pytest.raises(ValueError):
            WavSample.from_path(invalid).channels

        # valid with a section we don't add
        with path.open("wb") as stream:
            stream.write(b"RIFF")
            stream.write(struct.pack("<I", 54))
            stream.write(b"WAVE")

            stream.write(b"fmt ")
            stream.write(struct.pack("<IhhIIhh", 16, 1, 1, 1000, 4000, 4, 32))

            stream.write(b"LIST")
            stream.write(struct.pack("<I", 10))
            stream.write(b"1234567890")

            stream.write(b"data")
            stream.write(struct.pack("<I", 16))
            stream.write(struct.pack("<l", (2 ** 31) - 1))
            stream.write(struct.pack("<l", -((2 ** 31) - 1)))
            stream.write(struct.pack("<l", 0))
            stream.write(struct.pack("<l", 2 ** 30))

        sample = WavSample.from_path(path)
        assert sample.channels == 1
        assert round_samples(sample.load(1000, [1, 1, 1, 1])) == [
            (1,),
            (-1,),
            (0,),
            (0.5,),
        ]
