"""
Functions for generating different kinds of wave
"""

import math
from typing import Callable, Optional, Union

TWO_PI = math.pi * 2


def sine_wave(phase: float, /) -> float:
    """
    Return the value of a sine wave (bounded [-1, 1])

    phase: The position within the phase of the wave (as a
        ratio out of 1)
    """

    # always a good sign, we're going to special case some values that
    # get screwed up by rounding
    phase %= 1
    if phase == 0.5:
        return 0

    return math.sin(phase * TWO_PI)


def square_wave(phase: float, /) -> float:
    """
    Return the value of a square wave (bounded [-1, 1])

    phase: The position within the phase of the wave (as a
        ratio out of 1)
    """

    return -1 if (phase % 1) >= 0.5 else 1


def saw_wave(phase: float, /) -> float:
    """
    Return the value of a sawtooth wave (bounded [-1, 1])

    phase: The position within the phase of the wave (as a
        ratio out of 1)
    """

    return (4 * ((phase - 0.25) % 0.5)) - 1


def triangle_wave(phase: float, /) -> float:
    """
    Return the value of a triangle wave (bounded [-1, 1])

    phase: The position within the phase of the wave (as a
        ratio out of 1)
    """

    sample = (phase % 0.25) / 0.25

    if phase % 0.5 >= 0.25:
        sample = 1 - sample

    if phase % 1 >= 0.5:
        sample *= -1

    return sample


WAVES = {
    "sine": sine_wave,
    "square": square_wave,
    "saw": saw_wave,
    "triangle": triangle_wave,
}


class Waveform:
    """
    A wave that oscillates between [-1, 1] at a given frequency, & with
    a given shape.
    """

    def __init__(
        self,
        frequency: float,
        sample_rate: int,
        *,
        wave: Union[str, Callable[[float], float]] = sine_wave,
        phase: Optional[float] = None,
    ):
        """
        frequency: The frequency of the wave (in hz)
        sample_rate: How many samples to produce for each second
        wave: The shape of the wave (default sine). Can either be one of
            "sine", "square", "saw", or "triangle", or a function that
            takes a float value representing the phase (between [0–1))
            and returns an amplitude (between [-1, 1]).
        phase: If supplied, the previous phase position of the wave.
            Should be [0, 1).
        """
        self.frequency = frequency
        self.sample_rate = sample_rate

        if isinstance(wave, str):
            self.function = WAVES[wave]
        else:
            self.function = wave

        self.step = sample_rate / frequency

        if phase is None:
            self.offset = 0.0
            self.index = -1
        else:
            self.offset = phase
            self.index = 0

    @property
    def phase(self) -> Optional[float]:
        if self.index >= 0:
            return ((self.index / self.step) + self.offset) % 1

        return None

    def sample(self) -> float:
        self.index += 1
        return self.function((self.index / self.step) + self.offset)


__all__ = ("Waveform",)
