"""
Have instruments play through parts and bound them within a range.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import zip_longest
from typing import Generator

from blooper.instruments import Instrument
from blooper.parts import Part


@dataclass(frozen=True)
class Mixer:
    """
    A class that takes one or more parts and mixes them together into a
    single bounded output.
    """

    instruments: tuple[Instrument, ...]
    parts: tuple[Part, ...]
    volumes: tuple[float, ...]

    @classmethod
    def solo(cls, instrument: Instrument, part: Part, volume: float = 1) -> Mixer:
        """
        Create a 'mix' for a single instrument and part

        instrument: the instrument to mix
        part: the piece being played by the instrument
        volume: the volume to mix the instrument at
        """

        return cls((instrument,), (part,), (volume,))

    @classmethod
    def even(cls, *inputs: tuple[Instrument, Part], volume: float = 1) -> Mixer:
        """
        Evenly mix several instruments togetehrs

        inputs: Any number of instrument, part pairs.
        volume: the global volume to split evenly among instruments
        """
        if len(inputs) == 0:
            raise ValueError("You must mix at least one instrument")

        instruments = tuple(instrument for instrument, _ in inputs)
        parts = tuple(part for _, part in inputs)
        volumes = ((volume / len(inputs)),) * len(inputs)

        return cls(instruments, parts, volumes)

    def mix(
        self, sample_rate: int, channels: int, max_value: int
    ) -> Generator[tuple[int, ...], None, None]:
        """
        Mix all parts into a single bounded output

        sample_rate: how many samples per second
        channels: how many channels of audio to output
        max_value: The upper/lower bound for samples
        """

        for sample_sets in zip_longest(
            *(
                instrument.play(part, sample_rate, channels=channels)
                for instrument, part in zip(self.instruments, self.parts)
            )
        ):
            mixed = [0] * channels

            for sample_set, volume in zip(sample_sets, self.volumes):
                if sample_set is None:
                    continue

                for channel, sample in enumerate(sample_set):
                    mixed[channel] += sample * max_value * volume

            yield tuple(
                max(-max_value, min(max_value, round(sample))) for sample in mixed
            )
