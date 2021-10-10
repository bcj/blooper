"""
Instruments! They combine signal generators and envelopes to make notes.
They read those notes from parts. Wild stuff
"""

from abc import ABC, abstractmethod
from itertools import chain, repeat
from typing import Callable, Generator, Iterable, Iterator, Optional

from blooper.dynamics import AttackDecaySustainRelease, DynamicRange, Envelope
from blooper.parts import Part
from blooper.pitch import Tuning
from blooper.waveforms import Waveform


def then_zeroes(iterable: Iterable[float]) -> Iterator[float]:
    """
    Iterate over an (float) iterable and then repeat zeros forever
    """
    return chain(iterable, repeat(0.0))


class Instrument(ABC):
    """
    A tool for converting a part into a continuous array of samples
    given a set of the properties of the instrument itself.
    """

    @property
    @abstractmethod
    def tuning(self) -> Tuning:
        """
        The tuning the instrument is using
        """

    @classmethod
    def mono_to_stereo(cls, sample: float, balance: float) -> tuple[float, float]:
        """
        Convert a mono sample into a stereo sample.

        sample: The mono sample.
        balance: The left/right balance. 0 is even, -1 is all left, 1 is
            all right. left + right will always equal the mono input.
        """

        left = sample * (1 - balance) / 2
        right = sample * (1 + balance) / 2

        return left, right

    @abstractmethod
    def play(
        self, part: Part, sample_rate: int, *, channels: int = 2
    ) -> Generator[tuple[float, ...], None, None]:
        """
        Convert a part into a signal. Yields one sample at a time. Each
        sample _should_ be between [-1, 1] but it is not required

        part: The part to play
        sample_rate: The sample rate (in Hz).
        channels: How many channels of output to produce
        """


class Synthesizer(Instrument):
    """
    An instrument that plays parts by generating a Waveform.
    """

    def __init__(
        self,
        tuning: Tuning,
        *,
        wave: Optional[str | Callable[[float], float]] = "sine",
        balance: float = 0,
        envelope: Optional[Envelope] = None,
        dynamics: Optional[DynamicRange] = None,
    ):

        if wave is None:
            wave = "sine"

        if envelope is None:
            if dynamics is None:
                dynamics = DynamicRange()

            envelope = AttackDecaySustainRelease(dynamics)

        self._tuning = tuning
        self.wave = wave
        self.balance = balance
        self.envelope = envelope

    @property
    def tuning(self) -> Tuning:
        return self._tuning

    def play(
        self, part: Part, sample_rate: int, *, channels: int = 2
    ) -> Generator[tuple[float, ...], None, None]:

        if channels == 1:

            def fill_channels(sample: float) -> tuple[float, ...]:
                return (sample,)

        elif channels == 2:

            def fill_channels(sample: float) -> tuple[float, ...]:
                return self.mono_to_stereo(sample, self.balance)

        else:
            raise NotImplementedError(f"Unsupported channel count: {channels}")

        wave: Optional[Waveform] = None
        volumes: Iterable[float] = []
        index = 0
        start = 0.0

        for next_index, tone in part.tones(sample_rate):
            if index < next_index:
                if wave is None:
                    zero = (0,) * channels
                    for _ in range(next_index - index):
                        yield zero

                    index = next_index
                    start = 0
                else:
                    padded = then_zeroes(volumes)

                    for _ in range(next_index - index):
                        volume = next(padded)
                        start = wave.sample() * volume
                        yield fill_channels(start)

                    index = next_index
            else:
                start = 0

            frequency = self.tuning.pitch_to_frequency(tone.pitch)
            phase = None if wave is None else wave.phase
            wave = Waveform(frequency, sample_rate, wave=self.wave, phase=phase)
            volumes = self.envelope.volumes(tone, sample_rate, start)

        if wave is not None:
            for volume in self.envelope.volumes(tone, sample_rate, start):
                yield fill_channels(wave.sample() * volume)


__all__ = ("Instrument", "Synthesizer")
