"""
Classes that define the frequencies that correspond to notes
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from typing import Any, Optional

# just normal music stuff
SUBSCRIPTS = {
    "-": "₋",
    "0": "₀",
    "1": "₁",
    "2": "₂",
    "3": "₃",
    "4": "₄",
    "5": "₅",
    "6": "₆",
    "7": "₇",
    "8": "₈",
    "9": "₉",
}

MULTIPLIERS = {
    "double": 2,
    "triple": 3,
    "quadruple": 4,
    "quintuple": 5,
    "sextuple": 6,
    "septuple": 7,
    "octuple": 8,
}

# By putting the preferred symbol first in this list we'll use it when
# going the other way too
ACCIDENTAL_SYMBOLS = {
    "𝄫": Fraction(-1, 1),  # Look. I'm not happy about this either but it's true
    # unicode add sesquiflat you cowards
    "ȸ": Fraction(-3, 4),
    "♭": Fraction(-1, 2),
    "b": Fraction(-1, 2),
    # and demiflat
    "d": Fraction(-1, 4),
    "♮": Fraction(0, 1),
    # and demisharp
    "‡": Fraction(1, 4),  # close as we'll get for a symbol
    "♯": Fraction(1, 2),
    "#": Fraction(1, 2),
    # and sesquisharp
    "⩩": Fraction(3, 4),  # again, close enough
    "𝄪": Fraction(1, 1),
}

ACCIDENTAL_NAMES = {
    "sesquiflat": Fraction(-3, 4),
    "flat": Fraction(-1, 2),
    "demiflat": Fraction(-1, 4),
    "natural": Fraction(0, 1),
    "demisharp": Fraction(1, 4),
    "sharp": Fraction(1, 2),
    "sesquisharp": Fraction(3, 4),
}

DOUBLE_FLAT = ACCIDENTAL_SYMBOLS["𝄫"]
FLAT = ACCIDENTAL_NAMES["flat"]
NATURAL = ACCIDENTAL_NAMES["natural"]
SHARP = ACCIDENTAL_NAMES["sharp"]
DOUBLE_SHARP = ACCIDENTAL_SYMBOLS["𝄪"]


@cache
def accidental_symbol(accidental: Fraction) -> str:
    """
    Get the set of symbols that represents an accidental
    """
    fractions: dict[Fraction, str] = {}
    for symbol, fraction in ACCIDENTAL_SYMBOLS.items():
        if bool(fraction) == bool(accidental) and (fraction > 0) == (accidental > 0):
            fractions.setdefault(abs(fraction), symbol)

    symbols = []
    current = abs(accidental)

    if current in fractions:
        symbols.append(fractions[current])
        current = Fraction(0, 1)
    else:
        for fraction, symbol in sorted(fractions.items(), reverse=True):
            while current and fraction <= current:
                symbols.append(symbol)
                current -= fraction

            if not current:
                break

    if current:
        raise ValueError(f"Unable to express {accidental} symbolically")

    return "".join(symbols)


@dataclass(frozen=True)
class Pitch:
    """
    A musical pitch. Pitches can't be compared across scales and tunings
    and are not even meaningful outside of a scale and tunings context.
    Don't worry, this isn't really a problem.

    If you're using a chromatic scale (you probably are), you can use
    the `new` constructor and not have to think about microtonality.

    order: If you're using a chromatic scale, you can read this as
        octave. By convention, middle C would be 4, and the C one octave
        above it would be 5. Order isn't going to actually be tied to
        a specific frequency range until Tuning though.
    pitch_class: The letter or symbol associated with the pitch. If you
        are writing western music, this will probably be CDEFGAB. Which
        symbols are used is defined by Scale.
    accidental: The offset from the pitch class (e.g., sharp, flat).
        Supplied as a fraction which does not have a meaning outside of
        scale. The chromatic scale uses semitones so flat is -1/2 and
        sharp is 1/2. You can use the symbols/words instead of a
        fraction if you use the `new` constructor.
    """

    order: int
    pitch_class: str
    accidental: Optional[Fraction] = None

    @property
    def concurrence(self):
        return 1

    @classmethod
    def new(
        cls,
        order: int,
        pitch_class: str,
        accidental: Optional[str] = None,
    ) -> Pitch:
        """
        Create a new pitch.

        order: The octave* of the pitch. By convention, middle C would
            be 4, and the C one octave above it would be 5.
        pitch_class: Probably one of CDEFGAB*.
        accidental: the symbol(s) or name of the accidental (e.g., ♯, #,
            sharp). Symbols can be repeated as long as they're
            consistent. Defaults to natural

        * assuming a chromatic scale (or an Arab scale)
        """
        if accidental is None:
            fraction = None
        else:
            try:
                match = re.search(r"^(?:(\w+)[- ])?(\w+)$", accidental.lower())

                if match and match.group(2) in ACCIDENTAL_NAMES:
                    multiplier_word, accident = match.groups()

                    fraction = ACCIDENTAL_NAMES[accident]

                    if multiplier_word:
                        if not fraction:
                            raise ValueError("multiplying a natural doesn't make sense")

                        fraction *= MULTIPLIERS[multiplier_word]
                else:
                    # We're dissallowing mixing sharps/flats or adding
                    # unneeded naturals and we're requiring sharps/flats
                    # to be printed largest-to-smallest. We are however
                    # allowing different symbols to be used for the same
                    # value e.g., b & ♭ and note reducing (e.g;, 𝄫♭♭)
                    fraction = last = ACCIDENTAL_SYMBOLS[accidental[0]]

                    if fraction == 0 and len(accidental) > 1:
                        raise ValueError("Can't mix naturals with other symbols")

                    for symbol in accidental[1:]:
                        current = ACCIDENTAL_SYMBOLS[symbol]

                        if current == 0:
                            raise ValueError("Can't mix naturals with other symbols")

                        if (current > 0) != (fraction > 0):
                            raise ValueError("Can't mix sharps and flats")

                        if abs(current) > abs(last):
                            raise ValueError(
                                "Please supply sharps/flats in decreasing magnitude"
                            )

                        fraction += current
                        last = current
            except Exception as exception:
                # reraising to give consistent exception type
                raise ValueError(
                    f"Error while parsing symbol: {exception!r}"
                ) from exception

        return Pitch(order, pitch_class, fraction)

    def __str__(self) -> str:
        # left as an exercise for the reader: from_str
        order = "".join(SUBSCRIPTS[c] for c in str(self.order))
        if self.accidental is None:
            symbol = ""
        else:
            symbol = accidental_symbol(self.accidental)

        return f"{self.pitch_class}{order}{symbol}"


class Chord:
    """
    A collection of pitches to play in unison
    """

    def __init__(self, *pitches: Pitch):
        self.pitches = set(pitches)

    @property
    def concurrence(self):
        return len(self.pitches)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Chord):
            return self.pitches == other.pitches
        elif isinstance(other, Pitch):
            return self.pitches == {other}

        return NotImplemented

    # todo: new(cls, *positions: int, key: Key, scale: Scale = CHROMATIC_SCALE)


# TODO: It is maybe worth considering how this interacts with Key.
# Consider a pentatonic scale. In our implementation, it would use the
# same scale as a chromatic scale (probably?) and you would pick an
# appropriate key and tonic? Would we need to flag something else?
@dataclass(frozen=True)
class Scale:
    """
    One complete cycle of pitch classes. You probably can just use
    CHROMATIC_SCALE.

    steps: How many distinct tones there are in one cycle. The chromatic
        scale has 12 and the Arab scale has 24.
    classes: A dict containing all pitch classes in a scale and their
        (0-indexed) step number. The chromatic scale uses 7 classes
        across its 12 steps.
    step_size: What portion of a tone each step increments by. The
        chromatic scale increments by semitones (1 / 2), the Arab scale
        increments by quartertones (1 / 4). Defaults to semitones.
    harmonic_ratio: The multiplicative factor required to convert a
        tone of a given pitch class to the next tone in the same pitch
        class (i.e., how much higher frequency C₅ is than C₄). The
        chromatic scale has a harmonic ratio of 2 which it refers to as
        an octave. Defaults to 2.

    NOTE: Converting a Pitch to a tone is not possible without supplying
    a tuning and temperament. Steps will only be equal in size with an
    equal temperament (and even then the steps will be equal on a
    logarithmic scale not a linear one).
    """

    steps: int
    classes: dict[str, int]
    step_size: Fraction = Fraction(1, 2)
    harmonic_ratio: int = 2

    # needed so we can cache position
    def __hash__(self) -> int:
        return hash(
            (
                self.steps,
                tuple(sorted(self.classes.items())),
                self.step_size,
                self.harmonic_ratio,
            )
        )

    @cache
    def position(self, pitch: Pitch) -> tuple[int, int]:
        """
        Get the order and step within an order for a given pitch.

        NOTE: accidentals mean that a pitches order may not match the
        returned pitch (e.g., C₄♭ would actually be in order 3).
        """
        accidental = pitch.accidental or Fraction(0, 1)

        if accidental % self.step_size:
            raise ValueError(
                f"Pitch {pitch} not offset by multiple of step size: {self.step_size}"
            )

        order = pitch.order
        step = self.classes[pitch.pitch_class] + (accidental // self.step_size)

        while step < 0:
            order -= 1
            step += self.steps

        while step >= self.steps:
            order += 1
            step -= self.steps

        return order, step

    def equal_temperament(self) -> list[float]:
        """
        Generate an equal temperament for the scale.

        NOTE: The temperament will always be one shorter than the number
        of steps in the scale (as the octave starts on the first step
        and the next cycle is always the harmonic ratio)
        """
        return [
            self.harmonic_ratio ** (step / self.steps) for step in range(1, self.steps)
        ]


CHROMATIC_SCALE = Scale(12, {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11})

ARAB_SCALE = Scale(
    24,
    {"C": 0, "D": 4, "E": 8, "F": 10, "G": 14, "A": 18, "B": 22},
    step_size=Fraction(1, 4),
)

BOHLEN_PIERCE_SCALE = Scale(
    13,
    {"C": 0, "D": 2, "E": 3, "F": 4, "G": 6, "H": 7, "J": 9, "A": 10, "B": 12},
    harmonic_ratio=3,
)

JUST_BOHLEN_PIERCE = [
    27 / 25,
    25 / 21,
    9 / 7,
    7 / 5,
    75 / 49,
    5 / 3,
    9 / 5,
    49 / 25,
    15 / 7,
    7 / 3,
    63 / 25,
    25 / 9,
]


class Tuning:
    """
    How to convert the frequency of a supplied pitch into a frequency.
    """

    def __init__(
        self,
        pitch: Pitch,
        frequency: float,
        *,
        scale: Scale = CHROMATIC_SCALE,
        temperament: Optional[list[float]] = None,
    ):
        """
        Tune by supplying a concrete frequency to tie a note to and and
        then calculating any other note by its position relative to that
        supplied note.

        Assumes both a chromatic scale and an equal temperament unless
        otherwise provided.
        """
        if temperament is None:
            temperament = scale.equal_temperament()

        self.standard_pitch = pitch
        self.standard_frequency = frequency
        self.scale = scale
        self.temperament = temperament

        order, step = self.scale.position(pitch)
        self.standard_step = step

        if step != 0:
            frequency /= self.temperament[step - 1]

        self.order = order
        self.frequency = frequency

    # needed so we can cache pitch_to_frequency
    def __hash__(self) -> int:
        return hash(
            (
                self.standard_pitch,
                self.standard_frequency,
                self.scale,
                tuple(self.temperament),
            )
        )

    @cache
    def pitch_to_frequency(self, pitch: Pitch) -> float:
        """
        Calculate the frequency of a supplied pitch
        """
        # this skips equivalent pitches but that's fine because they'll
        # be caught in the standard step skip.
        if pitch == self.standard_pitch:
            return self.standard_frequency

        order, step = self.scale.position(pitch)

        if step == self.standard_step:
            frequency = self.standard_frequency
            step = 0
        else:
            frequency = self.frequency

        if order != self.order:
            frequency *= self.scale.harmonic_ratio ** (order - self.order)

        if step != 0:
            frequency *= self.temperament[step - 1]

        return frequency


A440 = Tuning(Pitch(4, "A"), 440)


__all__ = (
    "A440",
    "ARAB_SCALE",
    "CHROMATIC_SCALE",
    "BOHLEN_PIERCE_SCALE",
    "DOUBLE_FLAT",
    "DOUBLE_SHARP",
    "FLAT",
    "JUST_BOHLEN_PIERCE",
    "NATURAL",
    "SHARP",
    "Chord",
    "Pitch",
    "Scale",
    "Tuning",
    "accidental_symbol",
)
