"""
Instruments! They combine signal generators and envelopes to make notes.
They read those notes from parts. Wild stuff
"""
from __future__ import annotations

import json
import math
from abc import ABC, abstractmethod
from collections import defaultdict
from functools import cache
from itertools import chain, islice, repeat, zip_longest
from pathlib import Path
from random import choice
from typing import Callable, Generator, Iterable, Iterator, Optional

from blooper.dynamics import AttackDecaySustainRelease, DynamicRange, Envelope
from blooper.filetypes import SampleFile, UsageMetadata
from blooper.notes import Dynamic
from blooper.parts import Part
from blooper.pitch import A440, Tuning
from blooper.waveforms import Waveform

# Distance in cents
MAX_DISTANCE = 20


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

    @classmethod
    def stereo_to_mono(cls, left: float, right: float, balance: float) -> tuple[float]:
        """
        Convert a stereo sample into a mono sample.

        left: The left sample.
        right: The right sample.
        balance: The left/right balance. 0 is even, -1 is all left, 1 is
            all right. left + right will always equal the mono input.
        """

        return (((left * (1 - balance)) + (right * (1 + balance))) / 2,)

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
        wave: Optional[str | Callable[[float], float]] = "sine",
        *,
        balance: float = 0,
        tuning: Tuning = A440,
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

        waves: list[Waveform] = []
        volumes: Iterable[float] = []
        index = 0
        start = 0.0

        for next_index, tone in part.tones(sample_rate):
            if index < next_index:
                if not waves:
                    zero = (0,) * channels
                    for _ in range(next_index - index):
                        yield zero

                    index = next_index
                    start = 0.0
                else:
                    padded = then_zeroes(volumes)

                    for _ in range(next_index - index):
                        volume = next(padded)
                        start = sum(wave.sample() for wave in waves) * volume
                        yield fill_channels(start)

                    index = next_index
            else:
                start = 0

            old_waves = waves
            waves = []
            for pitch, old_wave in zip_longest(tone.pitches, old_waves):
                if pitch is None:
                    break

                waves.append(
                    Waveform(
                        self.tuning.pitch_to_frequency(pitch),
                        sample_rate,
                        wave=self.wave,
                        phase=old_wave.phase if old_wave else None,
                    )
                )

            volumes = self.envelope.volumes(tone, sample_rate, start)

        if waves:
            for volume in self.envelope.volumes(tone, sample_rate, start):
                yield fill_channels(sum(wave.sample() for wave in waves) * volume)


class Sampler(Instrument):
    """
    An instrument which plays notes using pre-recorded samples
    """

    def __init__(
        self,
        samples: dict[Path, UsageMetadata],
        *,
        tuning: Tuning = A440,
        envelope: Optional[Envelope] = None,
        dynamics: Optional[DynamicRange] = None,
        balance: float = 0,
        loop: bool = True,
        max_distance: float = MAX_DISTANCE,
        sample_format: str = "wav",
    ):
        if envelope is None:
            if dynamics is None:
                dynamics = DynamicRange()

            envelope = AttackDecaySustainRelease(dynamics)

        self._tuning = tuning
        self.envelope = envelope
        self.balance = balance
        self.loop = loop
        self.max_distance = max_distance
        self.samples = self.map_samples(samples, sample_format)

    @property
    def tuning(self) -> Tuning:
        return self._tuning

    @cache
    def compatible_samples(
        self, frequency: float, sample_rate: int, dynamic: Optional[Dynamic] = None
    ) -> set[SampleFile]:
        """
        Return the list of all compatible samples for a given frequency
        and sample rate
        """
        distance = None
        closest: set[SampleFile] = set()

        # we could make this all more efficient, who cares
        for actual_rate, samples_at_rate in self.samples.items():
            if actual_rate < sample_rate or actual_rate % sample_rate:
                continue

            for actual_frequency, samples in samples_at_rate.items():
                samples = {
                    sample
                    for sample in samples
                    if sample.usage_metadata.compatible_dynamic(dynamic)
                }

                if not samples:
                    continue

                if frequency == actual_frequency:
                    if distance == 0:
                        closest = closest.union(samples)
                    else:
                        distance = 0.0
                        closest = set(samples)
                elif distance == 0:
                    continue

                # We've claimed math elsewhere was acurate to 12 decimal places
                # so we'll replicate that here. It's low stakes to round or not
                # but this makes it easier to test we _can_ grab differing
                # frequencies if they're equidistant. Is that actually even
                # good? that means two notes played together can be off by
                # twice the cents we want and be played together. Hmm.
                actual_distance = round(
                    abs(1200 * math.log2(actual_frequency / frequency)), 12
                )
                if actual_distance > self.max_distance:
                    continue

                if distance is None or actual_distance < distance:
                    distance = actual_distance
                    closest = set(samples)
                elif distance == actual_distance:
                    closest = closest.union(samples)

        return closest

    def play(
        self, part: Part, sample_rate: int, *, channels: int = 2
    ) -> Generator[tuple[float, ...], None, None]:

        mixer: dict[int, Callable[[tuple[float, ...]], tuple[float, ...]]] = {}

        @cache
        def matching_channels(samples: tuple[float, ...]) -> tuple[float, ...]:
            return samples

        if channels == 1:
            mixer[1] = matching_channels

            @cache
            def stereo_to_mono(samples: tuple[int, int]) -> tuple[float]:
                left, right = samples
                return self.stereo_to_mono(left, right, self.balance)

            mixer[2] = stereo_to_mono
        elif channels == 2:

            @cache
            def mono_to_stereo(samples: tuple[int]) -> tuple[float, float]:
                return self.mono_to_stereo(samples[0], self.balance)

            mixer[1] = mono_to_stereo
            mixer[2] = matching_channels

        else:
            raise NotImplementedError(f"Unsupported channel count: {channels}")

        signals: list[Iterable[tuple[float, ...]]] = []
        functions: list[Callable[[tuple[float, ...]], tuple[float, ...]]] = []
        index = 0
        volumes: Iterable[float] = []
        start = 0.0
        zero = (0,) * channels

        for next_index, tone in part.tones(sample_rate):
            while index < next_index:
                if signals:
                    for sample_sets, volume in zip(
                        zip_longest(
                            *[islice(signal, next_index - index) for signal in signals]
                        ),
                        volumes,
                    ):
                        total = [0.0] * channels
                        for set_index, samples in enumerate(sample_sets):
                            if samples:
                                for channel, value in enumerate(
                                    functions[set_index](samples)
                                ):
                                    total[channel] += value

                        yield tuple(total)
                        index += 1
                        start = volume
                    signals = []
                    functions = []
                else:
                    for _ in range(next_index - index):
                        yield zero

                    index = next_index
                    start = 0

            signals = []
            functions = []
            # Used just for keeping track of start volume
            volumes = self.envelope.volumes(tone, sample_rate, start)

            for pitch in tone.pitches:
                frequency = self.tuning.pitch_to_frequency(pitch)
                compatible = list(
                    self.compatible_samples(frequency, sample_rate, tone.dynamic)
                )

                if compatible:
                    sample = choice(compatible)
                    signal = sample.load(
                        sample_rate,
                        self.envelope.volumes(tone, sample_rate, start),
                        loop=self.loop,
                    )
                    signals.append(signal)
                    functions.append(mixer[sample.channels])

        if signals:
            for sample_sets in zip_longest(*signals):
                total = [0.0] * channels
                for set_index, samples in enumerate(sample_sets):
                    if samples:
                        for channel, value in enumerate(functions[set_index](samples)):
                            total[channel] += value

                        yield tuple(total)

    @staticmethod
    def map_samples(
        sample_paths: dict[Path, UsageMetadata], sample_format: str
    ) -> dict[int, dict[float, set[SampleFile]]]:
        if sample_format == "wav":
            # love to avoid circular imports
            from blooper.wavs import WavSample as SampleClass
        else:
            raise NotImplementedError(f"Unsupported sample format: {sample_format}")

        # sort samples by sample rate then frequency. There may be
        # multiple samples that match.
        samples: dict[int, dict[float, set[SampleFile]]] = defaultdict(
            lambda: defaultdict(set)
        )

        for path, metadata in sample_paths.items():
            sample = SampleClass.from_path(path, metadata=metadata)

            samples[sample.sample_rate][metadata.frequency].add(sample)

        return samples

    @classmethod
    def from_file(
        cls,
        path: Path,
        *,
        tuning: Tuning = A440,
        envelope: Optional[Envelope] = None,
        dynamics: Optional[DynamicRange] = None,
        balance: float = 0,
        loop: bool = True,
        max_distance: float = MAX_DISTANCE,
    ) -> Sampler:
        with path.open("r") as stream:
            data = json.load(stream)

        sample_paths = {}
        for sample in data["samples"]:
            frequency = sample["frequency"]
            sample_path = Path(sample["path"])

            if not sample_path.is_absolute():
                sample_path = path.parent / sample_path

            minimum_volume = None
            if "minimum-volume" in sample:
                minimum_volume = Dynamic.from_name(sample["minimum-volume"])
            elif "min-volume" in sample:
                minimum_volume = Dynamic.from_symbol(sample["min-volume"])

            maximum_volume = None
            if "maximum-volume" in sample:
                maximum_volume = Dynamic.from_name(sample["maximum-volume"])
            elif "max-volume" in sample:
                maximum_volume = Dynamic.from_symbol(sample["max-volume"])

            sample_paths[sample_path] = UsageMetadata(
                frequency, minimum_volume, maximum_volume
            )

        return Sampler(
            sample_paths,
            tuning=tuning,
            envelope=envelope,
            dynamics=dynamics,
            balance=balance,
            loop=loop,
            max_distance=max_distance,
            sample_format=data["format"],
        )


__all__ = ("Instrument", "Sampler", "Synthesizer")
