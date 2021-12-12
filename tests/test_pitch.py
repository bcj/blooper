from fractions import Fraction

import pytest


def test_accidental_symbol():
    from blooper.pitch import accidental_symbol

    # singular symbols
    assert accidental_symbol(Fraction(-1, 1)) == "𝄫"
    assert accidental_symbol(Fraction(-3, 4)) == "ȸ"
    assert accidental_symbol(Fraction(-1, 2)) == "♭"
    assert accidental_symbol(Fraction(-1, 4)) == "d"
    assert accidental_symbol(Fraction(0, 1)) == "♮"
    assert accidental_symbol(Fraction(1, 4)) == "‡"
    assert accidental_symbol(Fraction(1, 2)) == "♯"
    assert accidental_symbol(Fraction(3, 4)) == "⩩"
    assert accidental_symbol(Fraction(1, 1)) == "𝄪"

    # combining symbols
    assert accidental_symbol(Fraction(-15, 4)) == "𝄫𝄫𝄫ȸ"
    assert accidental_symbol(Fraction(-3, 2)) == "𝄫♭"
    assert accidental_symbol(Fraction(-9, 4)) == "𝄫𝄫d"
    assert accidental_symbol(Fraction(5, 4)) == "𝄪‡"
    assert accidental_symbol(Fraction(5, 2)) == "𝄪𝄪♯"
    assert accidental_symbol(Fraction(15, 4)) == "𝄪𝄪𝄪⩩"

    with pytest.raises(ValueError):
        accidental_symbol(Fraction(1, 3))


def test_pitch():
    from blooper.pitch import Pitch

    assert Pitch.new(4, "A") == Pitch(4, "A", None)

    # names
    assert Pitch.new(4, "A", "natural") == Pitch(4, "A", Fraction(0, 1))
    assert Pitch.new(4, "A", "sesquiflat") == Pitch(4, "A", Fraction(-3, 4))
    assert Pitch.new(4, "A", "double sharp") == Pitch(4, "A", Fraction(1, 1))
    assert Pitch.new(4, "A", "octuple-sharp") == Pitch(4, "A", Fraction(4, 1))

    # illegal names
    with pytest.raises(ValueError):
        Pitch.new(4, "A", "double natural")

    with pytest.raises(ValueError):
        Pitch.new(4, "A", "triplesharp")

    with pytest.raises(ValueError):
        Pitch.new(4, "A", "double ♭")

    with pytest.raises(ValueError):
        Pitch.new(4, "A", "fart")

    # not currently illegal
    assert Pitch.new(4, "A", "double demisharp") == Pitch(4, "A", Fraction(1, 2))

    # symbols
    assert Pitch.new(4, "A", "♮") == Pitch(4, "A", Fraction(0, 1))
    assert Pitch.new(4, "A", "ȸ") == Pitch(4, "A", Fraction(-3, 4))
    assert Pitch.new(4, "A", "𝄪") == Pitch(4, "A", Fraction(1, 1))

    # combined symbols
    assert Pitch.new(4, "A", "𝄪𝄪𝄪⩩") == Pitch(4, "A", Fraction(15, 4))
    assert Pitch.new(4, "A", "𝄫b") == Pitch(4, "A", Fraction(-3, 2))

    # ilegal symbols
    with pytest.raises(ValueError):
        Pitch.new(4, "A", "♮♮")

    with pytest.raises(ValueError):
        Pitch.new(4, "A", "𝄫♮")

    with pytest.raises(ValueError):
        Pitch.new(4, "A", "𝄫♯")

    with pytest.raises(ValueError):
        Pitch.new(4, "A", "♯𝄪")

    with pytest.raises(ValueError):
        Pitch.new(4, "A", "?")

    # converting to a string
    assert str(Pitch(4, "A")) == "A₄"
    assert str(Pitch(4, "A", Fraction(0, 1))) == "A₄♮"
    assert str(Pitch(-13, "C", Fraction(15, 4))) == "C₋₁₃𝄪𝄪𝄪⩩"
    assert str(Pitch(0, "J", Fraction(-1, 2))) == "J₀♭"


def test_chord():
    from blooper.pitch import FLAT, Chord, Pitch

    with pytest.raises(ValueError):
        Chord()

    assert Chord(Pitch(4, "A")) == Pitch(4, "A")
    assert Chord(Pitch(4, "A")) != Pitch(4, "A", FLAT)
    assert Chord(Pitch(4, "A")) != Chord(Pitch(4, "A"), Pitch("A", FLAT))
    assert Chord(Pitch(4, "A")) == Chord(Pitch(4, "A"), Pitch(4, "A"))
    assert Chord(Pitch(4, "A"), Pitch(4, "B")) == Chord(Pitch(4, "B"), Pitch(4, "A"))

    # Hate writing the NotImplemented part of == checks.
    assert Chord(Pitch(4, "A")) != (4, "A")

    # don't really care how repr looks. just don't want it to error
    assert "" != repr(Chord(Pitch(4, "A"), Pitch(5, "B")))


def test_scale():
    from blooper.pitch import (
        ARAB_SCALE,
        BOHLEN_PIERCE_SCALE,
        CHROMATIC_SCALE,
        FLAT,
        NATURAL,
        SHARP,
        Pitch,
        Scale,
    )

    assert CHROMATIC_SCALE.position(Pitch(4, "C")) == (4, 0)
    assert CHROMATIC_SCALE.position(Pitch(4, "C", NATURAL)) == (4, 0)
    assert CHROMATIC_SCALE.position(Pitch(4, "A")) == (4, 9)
    assert CHROMATIC_SCALE.position(Pitch(4, "A", FLAT)) == (4, 8)
    assert CHROMATIC_SCALE.position(Pitch(4, "A", SHARP)) == (4, 10)
    assert CHROMATIC_SCALE.position(Pitch(2, "E")) == CHROMATIC_SCALE.position(
        Pitch(2, "F", FLAT)
    )
    assert CHROMATIC_SCALE.position(Pitch(2, "E", SHARP)) == CHROMATIC_SCALE.position(
        Pitch(2, "F")
    )
    assert CHROMATIC_SCALE.position(Pitch(2, "F", Fraction(-3, 2))) == (2, 2)
    assert CHROMATIC_SCALE.position(Pitch(4, "C", FLAT)) == (3, 11)
    assert CHROMATIC_SCALE.position(Pitch(4, "C", Fraction(-5, 1))) == (3, 2)
    assert CHROMATIC_SCALE.position(Pitch(4, "C", Fraction(-31, 2))) == (1, 5)
    assert CHROMATIC_SCALE.position(Pitch(4, "B")) == (4, 11)
    assert CHROMATIC_SCALE.position(Pitch(4, "B", SHARP)) == (5, 0)
    assert CHROMATIC_SCALE.position(Pitch(4, "B", Fraction(5, 1))) == (5, 9)
    assert CHROMATIC_SCALE.position(Pitch(4, "B", Fraction(31, 2))) == (7, 6)

    with pytest.raises(Exception):
        CHROMATIC_SCALE.position(Pitch(4, "H"))

    solfege = Scale(
        12,
        {
            "Do": 0,
            "Di": 1,
            "Ra": 1,
            "Re": 2,
            "Ri": 3,
            "Me": 3,
            "Ma": 3,
            "Mi": 4,
            "Fa": 5,
            "Fi": 6,
            "Se": 6,
            "Sol": 7,
            "Si": 8,
            "Le": 8,
            "L0": 8,
            "La": 9,
            "Li": 10,
            "Te": 10,
            "Ta": 10,
            "Ti": 11,
        },
    )

    assert CHROMATIC_SCALE.position(Pitch(2, "E")) == solfege.position(Pitch(2, "Mi"))
    assert CHROMATIC_SCALE.position(Pitch(2, "E", SHARP)) == solfege.position(
        Pitch(2, "Fa")
    )
    assert solfege.position(Pitch(2, "Ma")) == solfege.position(Pitch(2, "Me"))

    for pitch_class in ARAB_SCALE.classes:
        for fraction in (Fraction(-1, 1), FLAT, Fraction(0, 1), SHARP, Fraction(1, 1)):
            chromatic_octave, chromatic_index = CHROMATIC_SCALE.position(
                Pitch(4, pitch_class, fraction)
            )
            arab_octave, arab_index = ARAB_SCALE.position(
                Pitch(4, pitch_class, fraction)
            )
            assert chromatic_octave == arab_octave
            assert chromatic_index * 2 == arab_index

    # you can't use accidentals smaller than the step size
    demisharp = Fraction(1, 4)
    assert ARAB_SCALE.position(Pitch(4, "C", demisharp)) == (4, 1)
    with pytest.raises(ValueError):
        CHROMATIC_SCALE.position(Pitch(4, "C", demisharp))

    assert BOHLEN_PIERCE_SCALE.position(Pitch(3, "J")) == (3, 9)
    assert BOHLEN_PIERCE_SCALE.position(Pitch(3, "J", SHARP)) == (3, 10)
    assert BOHLEN_PIERCE_SCALE.position(Pitch(3, "B", SHARP)) == (4, 0)

    # stealing numbers from this:
    # https://en.wikipedia.org/wiki/12_equal_temperament
    assert len(CHROMATIC_SCALE.equal_temperament()) == 11
    assert round(CHROMATIC_SCALE.equal_temperament()[0], 6) == 1.059463
    assert round(CHROMATIC_SCALE.equal_temperament()[10], 6) == 1.887749

    assert len(BOHLEN_PIERCE_SCALE.equal_temperament()) == 12


def test_tuning():
    from blooper.pitch import (
        ARAB_SCALE,
        BOHLEN_PIERCE_SCALE,
        FLAT,
        JUST_BOHLEN_PIERCE,
        NATURAL,
        SHARP,
        Pitch,
        Tuning,
    )

    twelve_tet = Tuning(Pitch(4, "A"), 440)
    twenty_four_tet = Tuning(Pitch(4, "A"), 440, scale=ARAB_SCALE)

    # taking numbers for standard tuning on wikipedia
    # https://en.wikipedia.org/wiki/Piano_key_frequencies
    assert twelve_tet.pitch_to_frequency(Pitch(4, "A")) == 440
    assert twelve_tet.pitch_to_frequency(Pitch(4, "B", Fraction(-1, 1))) == 440
    assert twelve_tet.pitch_to_frequency(Pitch(5, "A")) == 880
    assert twelve_tet.pitch_to_frequency(Pitch(1, "A")) == 55
    assert twelve_tet.pitch_to_frequency(Pitch(0, "A")) == 27.5
    assert twelve_tet.pitch_to_frequency(Pitch(-2, "A")) == 6.875
    assert round(twelve_tet.pitch_to_frequency(Pitch(4, "C")), 4) == 261.6256
    assert round(twelve_tet.pitch_to_frequency(Pitch(8, "C")), 4) == 4186.009
    assert round(twelve_tet.pitch_to_frequency(Pitch(3, "A", SHARP)), 4) == 233.0819
    assert round(twelve_tet.pitch_to_frequency(Pitch(3, "B", FLAT)), 4) == 233.0819

    for octave in range(5):
        for pitch_class in ARAB_SCALE.classes:
            for accidental in (FLAT, NATURAL, SHARP):
                pitch = Pitch(octave, pitch_class, accidental)

                assert twelve_tet.pitch_to_frequency(
                    pitch
                ) == twenty_four_tet.pitch_to_frequency(pitch)

    # Information on actually tuning to this scale is scarce. Originally
    # looked at the  tuning on the first instrument
    # http://www.huygens-fokker.org/bpsite/instruments.html
    # but the page seems like it is wrong on note names? It claims F₁ is
    # 440 and it goes from C₁ to G₂ but the frequencies given suggest
    # the lowest note is about two tritaves lower and the the highest
    # note one tritave higher than the tuning note.
    # looking at this page that gives many frequencies
    # http://www.transpectra.org/scale_info.html#scale_pitches
    # the tuning note should be C (the first step) not F (the fourth)
    # As the two supplied frequencies also appear on this page, it seems
    # most likely there is a discrepency in note names between either
    # that page and what I'm using or Bohlen's naming conventions as of
    # then and what I assume are the now-possibly-standard names.
    bp_et = Tuning(Pitch(3, "C", NATURAL), 440, scale=BOHLEN_PIERCE_SCALE)

    assert bp_et.pitch_to_frequency(Pitch(3, "C", NATURAL)) == 440
    assert bp_et.pitch_to_frequency(Pitch(2, "B", SHARP)) == 440
    assert bp_et.pitch_to_frequency(Pitch(4, "C", NATURAL)) == 1320
    assert bp_et.pitch_to_frequency(Pitch(3, "B", SHARP)) == 1320
    assert bp_et.pitch_to_frequency(Pitch(5, "C", NATURAL)) == 3960
    assert bp_et.pitch_to_frequency(Pitch(2, "C", NATURAL)) == 440 / 3

    assert round(bp_et.pitch_to_frequency(Pitch(0, "H", SHARP)), 2) == 32.04
    assert round(bp_et.pitch_to_frequency(Pitch(4, "C", SHARP)), 2) == 1436.4

    bp_just = Tuning(
        Pitch(3, "C", NATURAL),
        440,
        scale=BOHLEN_PIERCE_SCALE,
        temperament=JUST_BOHLEN_PIERCE,
    )

    # notes in the same pitch class as the tuning note should match exactly
    # between equal temperament and just intonation
    for pitch in (
        Pitch(3, "C", NATURAL),
        Pitch(2, "B", SHARP),
        Pitch(4, "C", NATURAL),
        Pitch(3, "B", SHARP),
        Pitch(5, "C", NATURAL),
        Pitch(2, "C", NATURAL),
    ):
        assert bp_just.pitch_to_frequency(pitch) == bp_et.pitch_to_frequency(pitch)

    # We could use the numbers in this table to work out exact frequencies
    # for a given tuning. I do not know how to do this though.
    # https://en.wikipedia.org/wiki/Bohlen%E2%80%93Pierce_scale#Intervals_and_scale_diagrams
    assert round(bp_just.pitch_to_frequency(Pitch(3, "C", SHARP)), 8) == round(
        440 * 27 / 25, 8
    )
    assert round(bp_just.pitch_to_frequency(Pitch(3, "A", NATURAL)), 8) == round(
        440 * 7 / 3, 8
    )
    assert round(bp_just.pitch_to_frequency(Pitch(3, "A", SHARP)), 8) == round(
        440 * 63 / 25, 8
    )
    assert round(bp_just.pitch_to_frequency(Pitch(4, "C", SHARP)), 8) == round(
        1320 * 27 / 25, 8
    )
