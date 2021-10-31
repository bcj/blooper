"""
Writing samples to WAV files
"""
from __future__ import annotations

import struct
from pathlib import Path
from typing import Any, BinaryIO, Generator, Iterable

from blooper.filetypes import SampleFile
from blooper.mixers import Mixer

FILE_HEADER = "<4sI4s"
CHUNK_HEADER = "<4sI"
FORMAT_CHUNK = "<hhIIhh"
SAMPLES = {16: "<h", 32: "<l", 64: "<q"}

SAMPLES_PER_SECOND = 24_000
FORMAT_TAG = 1  # No compression
BITS_PER_SAMPLE = 32


def record(
    path: Path,
    mixer: Mixer,
    *,
    channels: int = 2,
    sample_rate: int = SAMPLES_PER_SECOND,
    bits_per_sample: int = BITS_PER_SAMPLE,
):
    """
    Write a WAV file by having a single instrument play a part
    """
    sample_format = SAMPLES[bits_per_sample]
    max_value = (2 ** (bits_per_sample - 1)) - 1

    block_align = channels * bits_per_sample // 8
    bytes_per_second = sample_rate * block_align

    with path.open("wb") as stream:
        format_chunk = struct.pack(
            FORMAT_CHUNK,
            FORMAT_TAG,
            channels,
            sample_rate,
            bytes_per_second,
            block_align,
            bits_per_sample,
        )
        format_size = len(format_chunk)
        format_header = struct.pack(CHUNK_HEADER, b"fmt ", format_size)

        # skip reading file header and data header until we know the size
        stream.seek(struct.calcsize(FILE_HEADER))
        stream.write(format_header)
        stream.write(format_chunk)
        data_header_byte = stream.tell()
        stream.seek(struct.calcsize(CHUNK_HEADER), 1)

        samples = 0
        for sample_set in mixer.mix(sample_rate, channels, max_value):
            samples += 1

            for sample in sample_set:
                stream.write(struct.pack(sample_format, sample))

        data_size = samples * block_align
        data_header = struct.pack(CHUNK_HEADER, b"data", data_size)
        file_header = struct.pack(
            FILE_HEADER,
            b"RIFF",
            4 + len(format_header) + format_size + len(data_header) + data_size,
            b"WAVE",
        )

        stream.seek(0)
        stream.write(file_header)
        stream.seek(data_header_byte)
        stream.write(data_header)


class WavSample(SampleFile):
    def __init__(self, path: Path):
        self.path = path
        self._loaded = False

        self._channels: int
        self._sample_rate: int
        self._seek_point: int

    @property
    def channels(self) -> int:
        if not self._loaded:
            with self.path.open("rb") as stream:
                self._load(stream)

        return self._channels

    @property
    def sample_rate(self) -> int:
        if not self._loaded:
            with self.path.open("rb") as stream:
                self._load(stream)

        return self._sample_rate

    def _load(self, stream: BinaryIO):
        """
        Advance a WAV stream to the data section, setting all necessary
        values from the header.
        """
        # already loaded
        if self._loaded:
            stream.seek(self._seek_point)
            return

        chunk_id, chunk_size, wave_id = struct.unpack(
            FILE_HEADER, stream.read(struct.calcsize(FILE_HEADER))
        )

        if chunk_id != b"RIFF" or wave_id != b"WAVE":
            raise ValueError(f"Invalid file header: {chunk_id} {chunk_size} {wave_id}")

        chunk_id, chunk_size = struct.unpack(
            CHUNK_HEADER, stream.read(struct.calcsize(CHUNK_HEADER))
        )

        if chunk_id != b"fmt ":
            raise ValueError(f"Invalid chunk header: {chunk_id}")

        (
            format_tag,
            channels,
            sample_rate,
            bytes_per_second,
            block_align,
            bits_per_sample,
        ) = struct.unpack(FORMAT_CHUNK, stream.read(chunk_size))

        if format_tag != FORMAT_TAG or chunk_size != 16:
            raise NotImplementedError("Only supporting PCM wave files")

        if bytes_per_second != sample_rate * block_align:
            raise ValueError(
                "Invalid bytes_per_second: "
                f"{bytes_per_second} expected ({sample_rate * block_align})"
            )

        # Find the data chunk
        while True:
            chunk_id, chunk_size = struct.unpack(
                CHUNK_HEADER, stream.read(struct.calcsize(CHUNK_HEADER))
            )

            if chunk_id == b"data":
                break
            elif chunk_id == b"LIST":
                stream.read(chunk_size)

        num_samples = chunk_size // block_align

        self._channels = channels
        self._sample_rate = sample_rate
        self._block_align = block_align
        self._bits_per_sample = bits_per_sample
        self._num_samples = num_samples
        self._seek_point = stream.tell()

        self._loaded = True

    def load(
        self, sample_rate: int, volumes: Iterable[float], loop: bool = False
    ) -> Generator[tuple[float, ...], None, None]:
        with self.path.open("rb") as stream:
            self._load(stream)

            if self._sample_rate % sample_rate:
                raise ValueError(
                    "Incompatible sample rate. "
                    f"Expected {sample_rate} found {self._sample_rate}"
                )

            wave_range = (2 ** (self._bits_per_sample - 1)) - 1
            sample_format = SAMPLES[self._bits_per_sample]
            sample_ratio = self._sample_rate // sample_rate
            sample_size = self._block_align // self._channels

            sample_index = 0

            for volume in volumes:
                samples = [0] * self._channels
                count = 0

                while count < sample_ratio:
                    for channel in range(self._channels):
                        samples[channel] += struct.unpack(
                            sample_format, stream.read(sample_size)
                        )[0]

                    count += 1
                    sample_index += 1

                    if sample_index == self._num_samples:
                        if loop:
                            stream.seek(self._seek_point)
                            sample_index = 0
                        else:
                            break

                yield tuple(volume * sample / count / wave_range for sample in samples)

                if sample_index == self._num_samples:
                    break

    def __hash__(self) -> int:
        return hash(self.path)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, WavSample):
            return self.path == other.path

        return NotImplemented

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path!r})"

    @classmethod
    def from_path(cls, path: Path) -> WavSample:
        return cls(path)


__all__ = ("record", "WavSample")
