"""
Classes that define notes (as they appear in western musical notation),
including their dynamic and any (of the currently-supported) accents.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from functools import total_ordering
from typing import Any, Iterable, Optional

from blooper.pitch import Chord, Pitch

# This should eventually be rolled in with tempo as part of the mood of
# the piece. As it is, this is a sort of hacky solution for processing
# all temporal properties of accents prior to throwing information about
# note size away when converting from notes to durations. 0 / 1 will
# make all notes last the entirety of their space (which is what tenuto
# and slur do regardless). This fraction is how much to reduce the
# length of a standard note as a fraction of the smaller of the note's
# length or the length of a standard note (e.g., if the part is in X/4
# time, any notes smaller than a quarter note will be reduced by their
# length * this factor. Larger notes like a whole note will only be
# reduces by the length of a quarter note * this factor). Look, if
# you're actually fiddling with this directly just scroll down to where
# this value is used.
TAILOFF_FACTOR = Fraction(1, 4)


class Accent(Enum):
    ACCENT = ">"  # strong then quickly back off
    MARCATO = "^"  # accent + staccato
    SLUR = "⁔"
    STACCATO = "."  # half duration
    STACCATISSIMO = "▾"  # quarter duration
    TENUTO = "-"  # full length
    # Wow, how are we going to do this? With Gliss we'll have the
    # preceding note and can look ahead or something. Hmm.
    # TREMOLO = "≋"

    def can_follow(self, previous: Optional[Accent] = None) -> bool:
        """
        Check whether an accent can immediately follow a note with
        another accent.
        """
        return previous != Accent.SLUR or self in (Accent.TENUTO, Accent.SLUR)

    def long(self) -> bool:
        """
        Check whether the accent is allowed on notes larger than the
        beat size.
        """
        return self in (Accent.SLUR, Accent.TENUTO)


@dataclass(frozen=True)
@total_ordering
class Dynamic:
    """
    How loud a note or passage is supposed to be played. positive is on
    the forte side, negative is on the piano side.

    NOTE: converting to name/symbol and back is a lossy action in some
    cases! If you originally created the dynamic by name/symbol it's
    fine though.
    """

    value: int

    @property
    def step(self) -> int:
        return 10

    @property
    def name(self) -> str:
        # tie-break toward mp
        if self.value > 0:
            base = "fort"
            ending = "e"
        else:
            base = "pian"
            ending = "o"

        magnitude = abs(self.value)

        if magnitude < 10:
            return f"mezzo-{base}{ending}"
        elif magnitude < 20:
            return f"{base}{ending}"

        return f"{base}{'iss' * ((magnitude - 10) // 10)}imo"

    @property
    def symbol(self) -> str:
        base = "f" if self.value > 0 else "p"
        magnitude = abs(self.value)

        if magnitude < 10:
            return f"m{base}"

        return base * (magnitude // 10)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Dynamic):
            return self.value < other.value

        return NotImplemented

    @classmethod
    def from_name(self, name: str) -> Dynamic:
        match = re.search(r"^(mezzo-)?(piano|forte)$", name)

        if match:
            half, dynamic = match.groups()

            value = 5 if half else 10

            if dynamic == "piano":
                value *= -1

            return Dynamic(value)

        match = re.search(r"^(pian|fort)((?:iss)+)imo$", name)

        if match:
            dynamic, isses = match.groups()

            multiplier = -10 if dynamic == "pian" else 10

            return Dynamic(((len(isses) // 3) + 1) * multiplier)

        raise ValueError(name)

    @classmethod
    def from_symbol(self, symbol: str) -> Dynamic:
        match = re.search(r"^(m?)(p+|f+)$", symbol)

        if match:
            half, dynamic = match.groups()

            magnitude = 1 if dynamic[0] == "f" else -1

            if half:
                if len(dynamic) > 1:
                    raise ValueError(symbol)

                return Dynamic(5 * magnitude)

            return Dynamic(10 * len(dynamic) * magnitude)

        raise ValueError(symbol)


@dataclass(frozen=True)
class Tone:
    """
    A pitch + the properties of how that pitch should be played.
    """

    pitch: Pitch | Chord
    dynamic: Optional[Dynamic] = None
    accent: Optional[Accent] = None

    @property
    def concurrence(self) -> int:
        return self.pitch.concurrence

    @property
    def pitches(self) -> Iterable[Pitch]:
        yield from self.pitch.pitches


@dataclass(frozen=True)
class Note:
    """
    A musical note (as they are represented in western musical notation)
    """

    duration: Fraction  # As a fraction of a whole note
    tone: Tone

    @property
    def concurrence(self) -> int:
        return self.tone.concurrence

    def components(
        self,
        beat_size: Fraction,
        *,
        tailoff_factor: Fraction = TAILOFF_FACTOR,
    ) -> tuple[Fraction, Pitch | Chord, Optional[Dynamic], Optional[Accent]]:
        """
        Get the components of a note, resolving any temporal accents by
        changing the duration.
        """
        duration = self.duration
        accent = self.tone.accent

        regular_length = True

        if accent in (Accent.MARCATO, Accent.STACCATO):
            duration /= 2

            if accent == Accent.MARCATO:
                accent = Accent.ACCENT
            else:
                accent = None

            regular_length = False
        elif accent == Accent.STACCATISSIMO:
            duration /= 4
            accent = None
            regular_length = False
        elif accent == Accent.TENUTO:
            accent = None
            regular_length = False
        elif accent == Accent.SLUR:
            regular_length = False

        if regular_length:
            duration -= min(beat_size, duration) * tailoff_factor

        return duration, self.tone.pitch, self.tone.dynamic, accent

    @classmethod
    def new(
        cls,
        duration,
        pitch: Pitch | Chord,
        dynamic: Optional[Dynamic] = None,
        accent: Optional[Accent] = None,
    ) -> Note:
        return Note(duration, Tone(pitch, dynamic=dynamic, accent=accent))


@dataclass(frozen=True)
class Rest:
    """
    A rest (as they are represented in western musical notation)
    """

    duration: Fraction

    @property
    def concurrence(self) -> int:
        return 0


class Notes(ABC):
    """
    A combination of multiple notes/rests
    """

    @property
    @abstractmethod
    def concurrence(self) -> int:
        """
        How many pitches are played at once
        """

    @abstractmethod
    def count(self) -> int:
        """
        How many notes the Notes should count as
        """

    @abstractmethod
    def duration(self, beat_size: Fraction) -> Fraction:
        """
        How long the notes collectively span. beat_size will be the base
        note size of the measure.
        """

    @abstractmethod
    def notes(self, beat_size: Fraction) -> Iterable[Note | Rest]:
        """
        Iterate over notes in the collection.
        """


class Grace(Notes):
    """
    A note with a grace note attached.
    """

    def __init__(
        self, pitch: Pitch | Chord, note: Pitch | Chord | Tone | Note, divisor: int = 4
    ):
        """
        pitch: The pitch of the grace note
        note: The note to add the grace note to. If a tone is supplied
            instead of a note, the duration of the grace + note will be
            the beat size. This is done so that grace notes can be
            placed on tuplets
        divisor: grace note length will be note.duration / divisor

        NOTE: If note is longer than beat_size, grace note size will be
        based on beat size
        """
        self.grace_tone = Tone(pitch)

        if isinstance(note, (Pitch, Chord)):
            self.tone = Tone(note)
            self.note = None
        elif isinstance(note, Tone):
            self.tone = note
            self.note = None
        else:
            self.tone = note.tone
            self.note = note

        self.divisor = divisor

    @property
    def concurrence(self) -> int:
        return max(self.grace_tone.concurrence, self.tone.concurrence)

    def count(self) -> int:
        return 1

    def duration(self, beat_size: Fraction) -> Fraction:
        return self.note.duration if self.note else beat_size

    def notes(self, beat_size: Fraction) -> Iterable[Note | Rest]:
        if self.note:
            grace_duration = min(self.note.duration, beat_size) / self.divisor
            note_duration = self.note.duration - grace_duration
        else:
            grace_duration = beat_size / self.divisor
            note_duration = beat_size - grace_duration

        yield Note(grace_duration, self.grace_tone)
        yield Note(note_duration, self.tone)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Grace):
            return (
                self.grace_tone == other.grace_tone
                and self.tone == other.tone
                and self.note == other.note
                and self.divisor == other.divisor
            )

        return NotImplemented

    def __repr__(self) -> str:
        return (
            f"Grace({self.grace_tone!r}, "
            f"{self.note if self.note else self.tone!r}, "
            f"divisor={self.divisor})"
        )


class Tuplet(Notes):
    """
    A set of notes/rests that together equal the duration of a single
    beat.

    Any nested Notes will be passed the duration of a single element in
    this tuplet as beat size (i.e., it a triplet is nested in a triplet,
    each element the inner triplet will be 1/9th of a beat).
    """

    def __init__(self, *tones: Optional[Pitch | Chord | Tone | Notes]):
        if len(tones) < 2:
            raise ValueError("At least two notes are required for a tuplet")

        self.tones = [
            Tone(tone) if isinstance(tone, (Pitch, Chord)) else tone for tone in tones
        ]

    @property
    def concurrence(self) -> int:
        concurrence = 0
        for tone in self.tones:
            if tone is not None:
                concurrence = max(concurrence, tone.concurrence)

        return concurrence

    def count(self) -> int:
        return len(self.tones)

    def duration(self, beat_size: Fraction) -> Fraction:
        return beat_size

    def notes(self, beat_size: Fraction) -> Iterable[Note | Rest]:
        duration = beat_size / self.count()

        for tone in self.tones:
            if tone is None:
                yield Rest(duration)
            elif isinstance(tone, Tone):
                yield Note(duration, tone)
            else:
                yield from tone.notes(duration)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Tuplet):
            return self.tones == other.tones

        return NotImplemented


class Triplet(Tuplet):
    def __init__(
        self,
        a: Optional[Pitch | Chord | Tone | Notes],
        b: Optional[Pitch | Chord | Tone | Notes],
        c: Optional[Pitch | Chord | Tone | Notes],
        /,
    ):
        super().__init__(a, b, c)


__all__ = ("Accent", "Dynamic", "Grace", "Note", "Rest", "Tone", "Triplet", "Tuplet")
