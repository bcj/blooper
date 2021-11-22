from fractions import Fraction

import pytest


def test_parse_pitch():
    from blooper.cli import parse_pitch
    from blooper.pitch import FLAT, Pitch

    assert parse_pitch("") is None
    assert parse_pitch("-") is None
    assert parse_pitch("A4") == Pitch(4, "A")
    assert parse_pitch("A4b") == Pitch(4, "A", FLAT)
    assert parse_pitch("A4♭") == Pitch(4, "A", FLAT)
    assert parse_pitch("C16♭♭♭♭") == Pitch(16, "C", Fraction(-2, 1))
    assert parse_pitch("D-1♭") == Pitch(-1, "D", FLAT)

    for text in ("A", "4", "4A"):
        with pytest.raises(ValueError):
            parse_pitch(text)


def test_parse_note():
    from blooper.cli import parse_note
    from blooper.pitch import FLAT, Pitch

    assert parse_note("") == (1, None)
    assert parse_note("-") == (1, None)
    assert parse_note("2-") == (2, None)
    assert parse_note("1A4") == (1, Pitch(4, "A"))
    assert parse_note("3A4") == (3, Pitch(4, "A"))
    assert parse_note("2A4b") == (2, Pitch(4, "A", FLAT))
    assert parse_note("2D-1♭") == (2, Pitch(-1, "D", FLAT))

    for text in ("A", "4", "4A", "-2A1"):
        with pytest.raises(ValueError):
            parse_note(text)


def test_parse_key():
    from blooper.cli import parse_key
    from blooper.parts import KEYS

    for name, key in KEYS.items():
        assert parse_key(name) == key
        assert parse_key(name.lower()) == key
        assert parse_key(name.replace("♭", "b")) == key
        assert parse_key(name.replace("♯", "#")) == key
        assert parse_key(name.lower().replace("♭", "b")) == key

    with pytest.raises(ValueError):
        parse_key("J♭ Minor")
