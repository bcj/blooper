"""
Classes that define notes (as they appear in western musical notation),
including their dynamic and any (of the currently-supported) accents.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Optional

from blooper.pitch import Pitch


class Accent(Enum):
    ACCENT = ">"  # strong then quickly back off
    MARCATO = "^"  # accent + staccato
    STACCATO = "."  # half duration
    STACCATISSIMO = "▾"  # quarter duration
    TENUTO = "-"  # full length
    SLUR = "⁔"
    # Wow, how are we going to do this? With Gliss we'll have the
    # preceding note and can look ahead or something. Hmm.
    # TREMOLO = "≋"


@dataclass(frozen=True)
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
class Note:
    """
    A musical note (as they are represented in western musical notation)
    """

    duration: Fraction  # As a fraction of a whole note
    pitch: Pitch
    # As an accent on the specific note. Will not change the dynamic
    # going forward and will be played at the piece's current dynamic.
    dynamic: Optional[Dynamic] = None
    accent: Optional[Accent] = None


@dataclass(frozen=True)
class Rest:
    """
    A rest (as they are represented in western musical notation)
    """

    duration: Fraction


@dataclass(frozen=True)
class Tone:
    """
    A version of a Note with its duration defined in terms of samples
    not the fraction of a measure.

    NOTE: Unlike with Notes, dynamic is required. With Note it's
    considered optional because the part may specify its own dynamic.
    It is assumed that Tones aren't being used for composition.
    """

    duration: int
    pitch: Pitch
    dynamic: Dynamic
    accent: Optional[Accent] = None


__all__ = ("Accent", "Dynamic", "Note", "Rest", "Tone")
