"""
Writing samples to WAV files
"""

import struct
from pathlib import Path

from blooper.mixers import Mixer

FILE_HEADER = "<4sI4s"
CHUNK_HEADER = "<4sI"
FORMAT_CHUNK = "<hhIIhh"
SAMPLES = {16: "<h", 32: "<l", 64: "<q"}

SAMPLES_PER_SECOND = 24_000
FORMAT_TAG = 1  # No compression
BITS_PER_SAMPLE = 32


# TODO: Are most compositions going to be a single instrument and part?
#       If so, you should make an alternate function that takes those
#       and calls this.
# TODO: Would be nice to pull some of the logic out of this for testing.
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
    max_value = (2 ** bits_per_sample) - 1

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
            len(format_header) + format_size + len(data_header) + data_size,
            b"WAVE",
        )

        stream.seek(0)
        stream.write(file_header)
        stream.seek(data_header_byte)
        stream.write(data_header)


__all__ = ("record",)
