"""
Definitions of key signatures
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from typing import Iterable, Optional

from blooper.pitch import (
    DOUBLE_FLAT,
    DOUBLE_SHARP,
    FLAT,
    NATURAL,
    SHARP,
    Pitch,
    accidental_symbol,
)


# TODO: Still not sure if this and Scale interact in the way we want.
# TODO: change to: name, root (pitch_class, accidental), accidentals
@dataclass(frozen=True)
class Key:
    """
    The sets of flats and sharps (or other accidentals) defining all
    pitch classes in a scale.

    Any unspecificed class is assumed to be natural.
    """

    root: str
    major: bool
    accidentals: dict[str, Fraction]

    @property
    def name(self) -> str:
        accidental = self.accidental(self.root)
        if accidental:
            root = f"{self.root}{accidental_symbol(accidental)}"
        else:
            root = self.root

        kind = "Major" if self.major else "Minor"

        return f"{root} {kind}"

    # needed so we can cache tone_to_step
    def __hash__(self) -> int:
        return hash((self.root, self.major, tuple(sorted(self.accidentals.items()))))

    @cache
    def accidental(self, pitch_class: str) -> Fraction:
        return self.accidentals.get(pitch_class, NATURAL)

    @cache
    def in_key(self, pitch: Pitch, accidental: Optional[Fraction] = None) -> Pitch:
        if pitch.accidental is None:
            if accidental is None:
                accidental = self.accidental(pitch.pitch_class)

            return Pitch(pitch.order, pitch.pitch_class, accidental)

        return pitch

    @classmethod
    def new(
        cls,
        root: str,
        major: bool,
        *,
        flats: Optional[Iterable[str]] = None,
        sharps: Optional[Iterable[str]] = None,
    ) -> Key:
        """
        Convenience method for creating keys.
        """

        accidentals = {}

        for pitch_classes, accidental in ((flats, FLAT), (sharps, SHARP)):
            if pitch_classes:

                for pitch_class in pitch_classes:
                    if pitch_class in accidentals:
                        raise ValueError(f"Pitch class specified twice: {pitch_class}")

                    accidentals[pitch_class] = accidental

        return cls(root, major, accidentals)


# TODO: something with related keys
# ALSO TODO: calculate these
KEYS = {
    # Relative: A minor
    # Parallel: C minor
    # Dominant: G major
    # Subdominent: F major
    "C Major": Key.new("C", True),
    # Relative: D minor
    # Parallel: F minor
    # Dominant: C major
    # Subdominant: B flat major
    "F Major": Key.new("F", True, flats=("B",)),
    # Relative: G minor
    # Parallel: B flat minor
    # Dominant: F major
    # Subdominant: E flat major
    "B♭ Major": Key.new("B", True, flats=("B", "E")),
    # Relative: C minor
    # Parallel: E flat minor
    # Dominant: B flat major
    # Subdominant: A flat major
    "E♭ Major": Key.new("E", True, flats=("E", "A", "B")),
    # Relative: F minor
    # Parallel: A flat minor, G sharp minor (enharmonic)
    # Dominant: E flat major
    # Subdominant: D flat major
    "A♭ Major": Key.new("A", True, flats=("A", "B", "D", "E")),
    # Relative B flat minor
    # Parallel key: D flat minor (theoretical), C sharp minor (enharmonic)
    # Dominant: A flat major
    # Subdominant G flat major
    # Enharmonic: C sharp major
    "D♭ Major": Key.new("D", True, flats=("D", "E", "G", "A", "B")),
    # Relative: E flat minor
    # Parallel: G flat minor (theoretical), F sharp minor (enharmonic)
    # Dominant: D flat major
    # Subdominant: C flat major, B major (enharmonic)
    # Enharmonic: F sharp major
    "G♭ Major": Key.new("G", True, flats=("G", "A", "B", "C", "D", "E")),
    # Relative: A flat minor, G sharp minor (enharmonic)
    # Parallel: C flat minor (theoretical), B minor (enharmonic)
    # Dominant: G flat major
    # Subdominant: F flat major, E major (enharmonic)
    # Enharmonic B major
    "C♭ Major": Key.new("C", True, flats=("C", "D", "E", "F", "G", "A", "B")),
    # Relative: D flat minor (theoretical), C sharp minor (enharmonic)
    # Parallel: F flat minor (theoretical), E minor (enharmonic)
    # Dominant: C flat major
    # Subdominant: B double-flat major (theoretical), A major (enharmonic)
    # Ehnharmonic E major
    "F♭ Major": Key(
        "F",
        True,
        {
            "F": FLAT,
            "G": FLAT,
            "A": FLAT,
            "B": DOUBLE_FLAT,
            "C": FLAT,
            "D": FLAT,
            "E": FLAT,
        },
    ),
    # Relative: E minor
    # Parlalel: G minor
    # Dominant: D major
    # Subdominant: C major
    "G Major": Key.new("G", True, sharps=("F",)),
    # Relative: B minor
    # Parallel: D minor
    # Dominant: A major
    # Subdominant: G major
    "D Major": Key.new("D", True, sharps=("F", "C")),
    # Relative: F sharp major
    # Parallel: A minor
    # Dominant: E major
    # Subdominant: D major
    "A Major": Key.new("A", True, sharps=("C", "F", "G")),
    # Relative: C sharp minor
    # Parallel: E minor
    # Dominant: B major
    # Subdominant: A major
    "E Major": Key.new("E", True, sharps=("F", "G", "C", "D")),
    # Relative: G sharp minor
    # Parallel: B minor
    # Dominant: F sharp major
    # Subdominant: E major
    # Enharmonic: C flat major
    "B Major": Key.new("B", True, sharps=("C", "D", "F", "G", "A")),
    # Relative: D sharp minor, E flat minor (enharmonic)
    # Parallel: F sharp minor
    # Dominant: C sharp major, D flat major (enharmonic)
    # Subdominant: B major
    # Enharmonic: G flat major
    "F♯ Major": Key.new("F", True, sharps=("F", "G", "A", "C", "D", "E")),
    # Relative: E sharp minor, F minor (enharmonic)
    # Parallel: G sharp minor
    # Dominant: D sharp major, E flat major (enharmonic)
    # Subdominant: C sharp major, D flat major (enharmonic)
    # Enharmonic: A flat major
    "G♯ Major": Key(
        "G",
        True,
        {
            "G": SHARP,
            "A": SHARP,
            "B": SHARP,
            "C": SHARP,
            "D": SHARP,
            "E": SHARP,
            "F": DOUBLE_SHARP,
        },
    ),
    "D♯ Major": Key(
        "D",
        True,
        {
            "D": SHARP,
            "E": SHARP,
            "F": DOUBLE_SHARP,
            "G": SHARP,
            "A": SHARP,
            "B": SHARP,
            "C": DOUBLE_SHARP,
        },
    ),
    "A♯ Major": Key(
        "A",
        True,
        {
            "A": SHARP,
            "B": SHARP,
            "C": DOUBLE_SHARP,
            "D": SHARP,
            "E": SHARP,
            "F": DOUBLE_SHARP,
            "G": DOUBLE_SHARP,
        },
    ),
    "E♯ Major": Key(
        "E",
        True,
        {
            "E": SHARP,
            "F": DOUBLE_SHARP,
            "G": DOUBLE_SHARP,
            "A": SHARP,
            "B": SHARP,
            "C": DOUBLE_SHARP,
            "D": DOUBLE_SHARP,
        },
    ),
    "B♯ Major": Key(
        "B",
        True,
        {
            "B": SHARP,
            "C": DOUBLE_SHARP,
            "D": DOUBLE_SHARP,
            "E": SHARP,
            "F": DOUBLE_SHARP,
            "G": DOUBLE_SHARP,
            "A": DOUBLE_SHARP,
        },
    ),
    # Relative: A sharp minor
    # Parallel: C sharp minor
    # Dominent: G sharp major (theoretical), A flat major (enharmonic)
    # Subdominent: F sharp major
    # Enharmonic: D flat major
    "C♯ Major": Key.new("C", True, sharps=("C", "D", "E", "F", "G", "A", "B")),
    # Relative: C major
    # Parallel: A major
    # Dominant: E minor
    # Subdominant: D minor
    "A Minor": Key.new("A", False),
    # Relative: F major
    # Parallel: D major
    # Dominant: A minor
    # Subdominant: G minor
    "D Minor": Key.new("D", False, flats=("B",)),
    # Relative: B flat major
    # Parallel: G major
    # Dominant: D minor
    # Subdominant: C minor
    "G Minor": Key.new("G", False, flats=("B", "E")),
    # Relative: E flat major
    # Parallel: C major
    # Dominant: G minor
    # Subdominant: F minor
    "C Minor": Key.new("C", False, flats=("E", "A", "B")),
    # Relative: A flat major
    # Parallel: F major
    # Dominant: C minor
    # Subdominant: B flat minor
    "F Minor": Key.new("F", False, flats=("A", "B", "D", "E")),
    # Relative: D flat major
    # Parallel: B flat major
    # Dominant: F minor
    # Subdominant: E flat minor
    # Enharmonic: A sharp minor
    "B♭ Minor": Key.new("B", False, flats=("B", "D", "E", "G", "A")),
    # Relative: G flat major
    # Parallel: E flat major
    # Dominant: B flat minor
    # Subdominant: A flat minor, G sharp minor (enharmonic)
    # Enharmonic: D sharp minor
    "E♭ Minor": Key.new("E", False, flats=("E", "G", "A", "B", "C", "D")),
    # Relative: C flat major, B major (enharmonic)
    # Parallel: A flat major
    # Dominant: E flat minor
    # Subdominant: D flat minor, C sharp minor (enharmonic)
    # Enharmonic: G sharp minor
    "A♭ Minor": Key.new("A", False, flats=("A", "B", "C", "D", "E", "F", "G")),
    # Relative: F flat major, E major (eharmonic)
    # Parallel: D flat major
    # Dominant: A flat minor, G sharp major (enharmonic)
    # Subdominant: G flat minor, F sharp minor (eharmonic)
    # Enharmonic: C sharp minor
    "D♭ Minor": Key(
        "D",
        False,
        {
            "D": FLAT,
            "E": FLAT,
            "F": FLAT,
            "G": FLAT,
            "A": FLAT,
            "B": DOUBLE_FLAT,
            "C": FLAT,
        },
    ),
    "G♭ Minor": Key(
        "G",
        False,
        {
            "G": FLAT,
            "A": FLAT,
            "B": DOUBLE_FLAT,
            "C": FLAT,
            "D": FLAT,
            "E": DOUBLE_FLAT,
            "F": FLAT,
        },
    ),
    "C♭ Minor": Key(
        "C",
        False,
        {
            "C": FLAT,
            "D": FLAT,
            "E": DOUBLE_FLAT,
            "F": FLAT,
            "G": FLAT,
            "A": DOUBLE_FLAT,
            "B": DOUBLE_FLAT,
        },
    ),
    "F♭ Minor": Key(
        "F",
        False,
        {
            "F": FLAT,
            "G": FLAT,
            "A": DOUBLE_FLAT,
            "B": DOUBLE_FLAT,
            "C": FLAT,
            "D": DOUBLE_FLAT,
            "E": DOUBLE_FLAT,
        },
    ),
    # Relative: G major
    # Parallel: E major
    # Dominant: B minor
    # Subdominant: A minor
    "E Minor": Key.new("E", False, sharps=("F",)),
    # Relative: D major
    # Parallel: B major
    # Dominant: F sharp minor
    # Subdominant: E minor
    "B Minor": Key.new("B", False, sharps=("C", "F")),
    # Relative: A major
    # Parallel: F sharp major, G flat major (enharmonic)
    # Dominant: C sharp minor
    # Subdominant: B minor
    "F♯ Minor": Key.new("F", False, sharps=("F", "G", "C")),
    # Relative: E major
    # Parallel: C sharp major, D flat major (enharmonic)
    # Dominant: G sharp minor
    # Subdominant: F sharp minor
    "C♯ Minor": Key.new("C", False, sharps=("C", "D", "F", "G")),
    # Relative: B major
    # Parallel: G sharp major (theoretical), A flat major (enharmonic)
    # Dominant: D sharp minor
    # Subdominant: C sharp minor
    # Enharmonic: A flat minor
    "G♯ Minor": Key.new("G", False, sharps=("G", "A", "C", "D", "F")),
    # Relative: F sharp major, G flat major (enharmonic)
    # Parallel: D sharp major (theoretical), E flat major (enharmonic)
    # Dominant: A sharp minor, B flat minor (enharmonic)
    # Subdominant: G sharp minor
    # Enharmonic: E flat minor
    "D♯ Minor": Key.new("D", False, sharps=("D", "E", "F", "G", "A", "C")),
    # Relative: C sharp major, D flat major (enharmonic)
    # Parallel: A sharp major (theoretical), B flat major (enharmonic)
    # Dominant: E sharp minor, F minor (enharmonic)
    # Subdominant: D sharp minor, E flat minor (enharmonic)
    # Enharmonic: B flat minor
    "A♯ Minor": Key.new("A", False, sharps=("A", "B", "C", "D", "E", "F", "G")),
    # Relative: G sharp major, A flat major (enharmonic)
    # Parallel: E sharp major (theoretical), F major (enharmonic)
    # Dominant: B sharp minor, C minor (enharmonic)
    # Subdominant: A sharp minor, B flat minor (enharmonic)
    # Enharmonic: F minor
    "E♯ Minor": Key(
        "E",
        False,
        {
            "E": SHARP,
            "F": DOUBLE_SHARP,
            "G": SHARP,
            "A": SHARP,
            "B": SHARP,
            "C": SHARP,
            "D": SHARP,
        },
    ),
    "B♯ Minor": Key(
        "B",
        False,
        {
            "B": SHARP,
            "C": DOUBLE_SHARP,
            "D": SHARP,
            "E": SHARP,
            "F": DOUBLE_SHARP,
            "G": SHARP,
            "A": SHARP,
        },
    ),
}


__all__ = ("KEYS", "Key")
