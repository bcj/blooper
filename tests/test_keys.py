from fractions import Fraction

import pytest


def test_key():
    from blooper.parts import Key
    from blooper.pitch import FLAT, NATURAL, SHARP, Pitch

    key = Key("C", True, {})

    assert key.accidental("C") == NATURAL
    assert key.accidental("D") == NATURAL
    assert key.accidental("E") == NATURAL
    assert key.accidental("F") == NATURAL
    assert key.accidental("G") == NATURAL
    assert key.accidental("A") == NATURAL
    assert key.accidental("B") == NATURAL

    key = Key("C", True, {"G": Fraction(1, 1), "A": FLAT})

    assert key.accidental("C") == NATURAL
    assert key.accidental("D") == NATURAL
    assert key.accidental("E") == NATURAL
    assert key.accidental("F") == NATURAL
    assert key.accidental("G") == Fraction(1, 1)
    assert key.accidental("A") == FLAT
    assert key.accidental("B") == NATURAL

    key = Key.new("C", True)

    assert key.name == "C Major"
    assert key.accidental("C") == NATURAL
    assert key.accidental("D") == NATURAL
    assert key.accidental("E") == NATURAL
    assert key.accidental("F") == NATURAL
    assert key.accidental("G") == NATURAL
    assert key.accidental("A") == NATURAL
    assert key.accidental("B") == NATURAL

    key = Key.new("G", True, sharps=("F",))

    assert key.name == "G Major"
    assert key.accidental("C") == NATURAL
    assert key.accidental("D") == NATURAL
    assert key.accidental("E") == NATURAL
    assert key.accidental("F") == SHARP
    assert key.accidental("G") == NATURAL
    assert key.accidental("A") == NATURAL
    assert key.accidental("B") == NATURAL

    key = Key.new("A", True, sharps=("C", "F", "G"))

    assert key.name == "A Major"
    assert key.accidental("C") == SHARP
    assert key.accidental("D") == NATURAL
    assert key.accidental("E") == NATURAL
    assert key.accidental("F") == SHARP
    assert key.accidental("G") == SHARP
    assert key.accidental("A") == NATURAL
    assert key.accidental("B") == NATURAL

    key = Key.new("F", True, sharps=("F", "G", "A", "C", "D", "E"))

    assert key.name == "F♯ Major"
    assert key.accidental("C") == SHARP
    assert key.accidental("D") == SHARP
    assert key.accidental("E") == SHARP
    assert key.accidental("F") == SHARP
    assert key.accidental("G") == SHARP
    assert key.accidental("A") == SHARP
    assert key.accidental("B") == NATURAL

    key = Key.new("B", False, flats=("B", "D", "E", "G", "A"))

    assert key.name == "B♭ Minor"
    assert key.accidental("C") == NATURAL
    assert key.accidental("D") == FLAT
    assert key.accidental("E") == FLAT
    assert key.accidental("F") == NATURAL
    assert key.accidental("G") == FLAT
    assert key.accidental("A") == FLAT
    assert key.accidental("B") == FLAT

    with pytest.raises(ValueError):
        Key.new("B", False, flats=("B", "D", "E", "G", "A", "A"))

    sharps = ("A", "B", "C")
    flats = ("D", "E")
    key = Key.new("X", False, sharps=sharps, flats=flats)
    for pitch_class in "ABCDEF":
        for accidental in (FLAT, NATURAL, SHARP):
            pitch = Pitch(4, pitch_class, accidental)
            assert key.in_key(pitch) == pitch

    for pitch_class in sharps:
        assert key.in_key(Pitch(3, pitch_class)) == Pitch(3, pitch_class, SHARP)

    for pitch_class in flats:
        assert key.in_key(Pitch(3, pitch_class)) == Pitch(3, pitch_class, FLAT)

    key.in_key(Pitch(3, "f")) == Pitch(3, "f", NATURAL)


def test_keys():
    from blooper.keys import KEYS

    for name, key in KEYS.items():
        assert name == key.name

    assert len(KEYS) == 42
