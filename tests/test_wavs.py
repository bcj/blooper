import struct


def test_wave_range():
    from blooper.wavs import wave_range

    assert wave_range(8) == (-127, 127)
    minimum, maximum = wave_range(16)
    assert struct.pack("<h", minimum) != struct.pack("<h", maximum)
