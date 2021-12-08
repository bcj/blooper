"""
Conversions from Dynamics to absolute volumes
"""

from abc import ABC, abstractmethod
from fractions import Fraction
from functools import cache
from typing import Any, Generator, Optional

from blooper.notes import Accent, Dynamic, Tone


class DynamicRange:
    """
    Prescribe volumes to Dynamics based on the expressible range an
    instrument has.
    """

    def __init__(
        self,
        minimum: Dynamic = Dynamic.from_name("pianissimo"),
        full: Dynamic = Dynamic.from_name("fortissimo"),
        maximum: Dynamic = Dynamic.from_name("fortissississimo"),
        minimum_output: float = 0.1,
        full_output: float = 1,
        maximum_output: float = 1.2,
    ):
        """
        minimum: The Dynamic representing the quietest dynamic an
            instrument can play. Any quieter dynamics will be played at
            the same volume as this dynamic.
        full: The Dynamic representing the loudest noise an instrument
            can play without clipping.
        maximum: The loudest dynamic an instrument can play. Any louder
            will be played at the same volume as this dynamic.
        minimum_output: How loud (as a ratio out of 1) the quietest
            dynamic should be played at.
        full_output: How loud (as a ratio out of 1) the loudest* dynamic
            should be played at.
        maximum_output: How loud (as a ratio out of 1) the loudest
            dynamic should be played at. This value may be larget than 1.
        """

        self.minimum = minimum.value
        self.full = full.value
        self.maximum = maximum.value

        if not (self.minimum <= self.full <= self.maximum):
            raise ValueError(f"Invalid dynamic values: {minimum}, {full}, {maximum}")

        self.minimum_output = minimum_output
        self.full_output = full_output
        self.maximum_output = maximum_output

        if not (minimum_output <= full_output <= maximum_output):
            raise ValueError(
                "Invalid output values: "
                f"{minimum_output}, {full_output}, {maximum_output}"
            )

        if self.minimum == self.full and minimum_output != full_output:
            raise ValueError("minimum and full dynamics match but volumes don't")

        if self.full == self.maximum and full_output != maximum_output:
            raise ValueError("full and maximum dynamics match but volumes don't")

    # needed because we provide __eq__ + use @cache?
    def __hash__(self) -> int:
        return hash(
            (
                self.minimum,
                self.full,
                self.maximum,
                self.minimum_output,
                self.full_output,
                self.maximum_output,
            )
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, DynamicRange):
            return (
                self.minimum == other.minimum
                and self.full == other.full
                and self.maximum == other.maximum
                and self.minimum_output == other.minimum_output
                and self.full_output == other.full_output
                and self.maximum_output == other.maximum_output
            )

        return NotImplemented

    @cache
    def volume(self, dynamic: Dynamic) -> float:
        """
        Get the volume associated with a dynamic
        """

        value = dynamic.value

        if value <= self.minimum:
            return self.minimum_output

        if value < self.full:
            return self.minimum_output + (
                (self.full_output - self.minimum_output)
                * ((value - self.minimum) / (self.full - self.minimum))
            )

        if value == self.full:
            return self.full_output

        if value >= self.maximum:
            return self.maximum_output

        return self.full_output + (
            (self.maximum_output - self.full_output)
            * ((value - self.full) / (self.maximum - self.full))
        )


class Envelope(ABC):
    """
    Provides the volume that each sample of a tone should play at
    """

    @property
    @abstractmethod
    def dynamics(self) -> DynamicRange:
        """
        The DynamicRange being used by the envelope
        """

    @abstractmethod
    def volumes(
        self, tone: Tone, sample_rate: int, start: float = 0
    ) -> Generator[float, None, None]:
        """
        Determine the amplitudes of each sample. Generator may produce
        more samples than the tone is supposed to contain (e.g., if
        there is a minimum envelope size), but will always be at least
        as long as the tone's duration (i.e., if the envelope cannot
        be sustained long enough, it will yield 0s until it reaches
        the duration).

        tone: The tone to produce amplitudes for. It is expected that
            the volumizer will handle any accents that effect volume
        sample_rate: How many samples are being produced a second.
        start: The starting amplitude (may be > 0 if the previous tone
            didn't finish before the current tone is set to start)
        """


class Homogeneous(Envelope):
    """
    An envelope where each tone is played with the requested dynamic but
    without any variation within each tone.

    Accents and starting amplitude have no bearing on the note being
    produced.
    """

    def __init__(self, dynamics: DynamicRange):
        self._dynamics = dynamics

    @property
    def dynamics(self) -> DynamicRange:
        return self._dynamics

    def volumes(
        self, tone: Tone, sample_rate: int, start: float = 0
    ) -> Generator[float, None, None]:
        volume = self.dynamics.volume(tone.dynamic)
        for _ in range(tone.duration):
            yield volume


class AttackDecaySustainRelease(Envelope):
    """
    An envelope with an attack, decay, sustain, and release steps.

    In this implementation attack/sustain/release have constant rates,
    so the length of these three steps will vary by volume.
    """

    def __init__(
        self,
        dynamics: DynamicRange,
        attack: float = 0.05,
        decay: Optional[float] = 0.025,
        release: Optional[float] = None,
        sustain_level: float = 0.8,
        accent_multiplier: float = 1,
        # Are you going to cave on this? It seems like a bad unit
        accent_peak: Fraction = Fraction(1, 2),
        accent_sustain_level: float = 0.8,
    ):
        """
        dynamics: The range for the envelope
        attack: The time (in seconds) required for the volume to go from
            0 to 1 during the attack phase. NOTE: The duration of this
            phase will only match this time if the starting volume is 0
            and initial peak volume is 1.
        decay: The time (in seconds) required for the volume to go from
            1 to 0 during the decay phase. If None, the attack will be
            used. NOTE: The duration of this phase will only match this
            time if the peak volume is 1 and the sustain level is 0.
        release: the time (in seconds) required for the volume to
            go from 1 to 0 during the release phase. If None, the decay
            will be used. NOTE: The duration of this phase will only
            match this time if the sustain volume is 1.
        sustain_level: How loud the sustain phase should be relative to
            its peak (this value is not a volume itself). The sustain
            volume will only equal the sustain level if the peak volume
            is 1.
        accent_multiplier: How much faster the attack/decay/release
            rates should be when playing a tone when the accent is
            Accent.ACCENT. A multiplier of 2 will make each phase half
            as long.
        accent_peak: How much louder (as a fractional step in dynamics)
            the peak of a tone should be if the tone's accent is
            Accent.ACCENT. A peak of 1 would make an accented forte tone
            fortissimo at its peak.
        accent_sustain_multiplier: What to multiply the base sustain
            level by for tones with the accent Accent.ACCENT. If 1, the
            same level will be used. NOTE: this level is still being
            applied to the original dynamic, not the dynamic once
            modified by accent_peak (i.e., if the dynamic is forte and
            accent_peak is that of fortissimo, sustain level will still
            be calculated as a percentage of the forte volume).
        """

        # todo: ensure values make sense
        if sustain_level > 1:
            raise ValueError(f"Cannot sustain higher than peak: {sustain_level}")

        if decay is None:
            decay = attack

        if release is None:
            release = decay

        if attack <= 0:
            raise ValueError(f"Attack duration must be positive: {attack}")

        if decay <= 0:
            raise ValueError(f"Decay duration must be positive: {decay}")

        if release <= 0:
            raise ValueError(f"Release duration must be positive: {release}")

        self._dynamics = dynamics

        self.attack = attack
        self.decay = decay
        self.release = release

        self.sustain_level = sustain_level

        self.accent_multiplier = accent_multiplier
        self.accent_peak = accent_peak
        self.accent_sustain_level = accent_sustain_level

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, AttackDecaySustainRelease):
            return (
                self.dynamics == other.dynamics
                and self.attack == other.attack
                and self.decay == other.decay
                and self.release == other.release
                and self.sustain_level == other.sustain_level
                and self.accent_peak == other.accent_peak
                and self.accent_sustain_level == other.accent_sustain_level
            )

        return NotImplemented

    @property
    def dynamics(self) -> DynamicRange:
        return self._dynamics

    def volumes(
        self, tone: Tone, sample_rate: int, start: float = 0
    ) -> Generator[float, None, None]:

        peak, sustain, end, attack_rate, decay_rate, release_rate = self._rates(
            tone, sample_rate
        )

        yield from self._volumes(
            tone.duration,
            start,
            peak,
            sustain,
            end,
            attack_rate,
            decay_rate,
            release_rate,
        )

    def _rates(
        self, tone: Tone, sample_rate: int
    ) -> tuple[float, float, float, float, float, float]:
        """
        Work out the rates max/min possible volumes for a tone. Split out
        just to make testing easier (esp. because the rest of volumes is a
        little bit of a nightmare)
        """
        peak = self.dynamics.volume(tone.dynamic)
        attack = self.attack * sample_rate
        decay = self.decay * sample_rate
        release = self.release * sample_rate

        sustain = self.sustain_level * peak
        end = 0.0

        if tone.accent == Accent.ACCENT:
            peak = self.dynamics.volume(
                Dynamic(
                    tone.dynamic.value + round(tone.dynamic.step * self.accent_peak)
                )
            )
            attack /= self.accent_multiplier
            decay /= self.accent_multiplier
            release /= self.accent_multiplier
        elif tone.accent == Accent.SLUR:
            end = sustain

        return peak, sustain, end, 1 / attack, 1 / decay, 1 / release

    @classmethod
    def _volumes(
        cls,
        duration: float,
        start: float,
        peak: float,
        sustain: float,
        end: float,
        attack_rate: float,
        decay_rate: float,
        release_rate: float,
    ) -> Generator[float, None, None]:
        # we may not have enough time for a full ADSR envelope. We will
        # always attack/decay/release at the expected rates. We will
        # always start at the start value and produce volumes until we
        # reach 0. Within these rules our priorities are:
        # • reach the end volume as close to the duration as possible
        # • attack until we reach as close to the expected peak without
        #   going over time.
        # • decay until we reach as close to the expected sustain
        #   without going over time.
        # • sustain at the sustain volume as long as we can without
        #   going overtime.
        # As such, the priority for the 4 stages is:
        # release > attack > decay > sustain

        remaining = duration

        volume = start
        if volume > end:
            release_samples = (start - end) * release_rate
        else:
            release_samples = 0

        if release_samples < remaining and start < peak:
            # if we attack until the exact moment we need to release
            # this formula will give us how loud the peak is.
            # if the peak is below sustain, above peak, or relase is
            # faster than decay, then we can use this to work out how
            # long to attack (if it's above sustain and decay is faster,
            # we actually can have a slightly higher peak):
            # remaining = ((peak - start) / attack_rate) + ((peak - end) / release_rate)
            # we can rearrange this to:
            max_peak = (
                attack_rate
                * release_rate
                * (remaining + (start / attack_rate) + (end / release_rate))
                / (release_rate + attack_rate)
            )

            if max_peak >= peak:
                actual_peak = peak
            elif max_peak <= sustain or release_rate >= decay_rate:
                actual_peak = max_peak
            else:
                # TODO: still a bug here. if attack doesn't land on the sustain
                # level exactly then we maybe are wrong?
                attack_decay_remaining = remaining - ((sustain - end) / release_rate)

                if start < sustain:
                    attack_decay_remaining -= (sustain - start) / attack_rate

                # same formula again but this time with decay
                # attack_decay_remaining =
                #    ((peak - sustain) / attack_rate) + ((peak - sustain) / decay_rate)
                # which rearranges to:
                max_peak = (
                    attack_rate
                    * decay_rate
                    * (
                        attack_decay_remaining
                        + (sustain / attack_rate)
                        + (sustain / decay_rate)
                    )
                    / (attack_rate + decay_rate)
                )

                actual_peak = min(peak, max_peak)

            if actual_peak > start:
                difference = actual_peak - start
                attack_samples = difference / attack_rate

                for index in range(round(attack_samples)):
                    yield start + (difference * (index + 1) / attack_samples)

                volume = actual_peak
                remaining -= round(attack_samples)

        if volume > sustain:
            if decay_rate >= release_rate:
                decayed = sustain
            else:
                # If we delay until the exact moment we would need to release
                # remaining =
                #   ((volume - decayed) / decay_rate) + ((decayed - end) / release_rate)
                # which we can rearrange to:
                decayed = (
                    decay_rate
                    * release_rate
                    * (remaining - (volume / decay_rate) + (end / release_rate))
                    / (decay_rate - release_rate)
                )

                if decayed < sustain:
                    decayed = sustain

            if decayed < volume:
                difference = volume - decayed
                decay_samples = difference / decay_rate

                for index in range(round(decay_samples)):
                    # TODO: if it is rounding up and we aren't sustaining then
                    # arguably we should be using a blend of decay and release
                    yield max(
                        sustain, volume - (difference * (index + 1) / decay_samples)
                    )

                volume = decayed
                remaining -= decay_samples

        release_samples = max(0.0, (volume - end) / release_rate)
        sustain_samples = round(remaining - release_samples)

        if sustain_samples > 0 and volume == sustain:
            for _ in range(sustain_samples):
                yield volume

            remaining -= sustain_samples

        release_samples = volume / release_rate
        for index in range(round(release_samples)):
            yield max(0.0, volume - (volume * (index + 1) / release_samples))

        padding = round(remaining - release_samples)
        if padding > 0:
            for _ in range(padding):
                yield 0.0


__all__ = ("AttackDecaySustainRelease", "DynamicRange", "Envelope", "Homogeneous")
