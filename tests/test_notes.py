from fractions import Fraction

import pytest


def test_accent():
    from blooper.notes import Accent

    ALL_ACCENTS = {
        Accent.ACCENT,
        Accent.MARCATO,
        Accent.SLUR,
        Accent.STACCATO,
        Accent.STACCATISSIMO,
        Accent.TENUTO,
    }
    AFTER_SLUR = {
        Accent.SLUR,
        Accent.TENUTO,
    }

    for accent in ALL_ACCENTS:
        assert accent.can_follow()

        for previous in ALL_ACCENTS - {Accent.SLUR}:
            assert accent.can_follow(previous)

        if accent in AFTER_SLUR:
            assert accent.can_follow(Accent.SLUR)
            assert accent.long()
        else:
            assert not accent.can_follow(Accent.SLUR)
            assert not accent.long()


def test_dynamic():
    from blooper.notes import Dynamic

    assert Dynamic(0).step == 10
    assert Dynamic(10).step == 10

    assert Dynamic(-40).name == "pianissississimo"
    assert Dynamic(-39).name == "pianississimo"
    assert Dynamic(-30).name == "pianississimo"
    assert Dynamic(-20).name == "pianissimo"
    assert Dynamic(-16).name == "piano"
    assert Dynamic(-10).name == "piano"
    assert Dynamic(-5).name == "mezzo-piano"
    assert Dynamic(0).name == "mezzo-piano"
    assert Dynamic(1).name == "mezzo-forte"
    assert Dynamic(10).name == "forte"
    assert Dynamic(19).name == "forte"
    assert Dynamic(20).name == "fortissimo"
    assert Dynamic(32).name == "fortississimo"
    assert Dynamic(40).name == "fortissississimo"

    assert Dynamic(-40).symbol == "pppp"
    assert Dynamic(-39).symbol == "ppp"
    assert Dynamic(-30).symbol == "ppp"
    assert Dynamic(-20).symbol == "pp"
    assert Dynamic(-16).symbol == "p"
    assert Dynamic(-10).symbol == "p"
    assert Dynamic(-5).symbol == "mp"
    assert Dynamic(0).symbol == "mp"
    assert Dynamic(1).symbol == "mf"
    assert Dynamic(10).symbol == "f"
    assert Dynamic(19).symbol == "f"
    assert Dynamic(20).symbol == "ff"
    assert Dynamic(32).symbol == "fff"
    assert Dynamic(40).symbol == "ffff"

    assert Dynamic.from_name("pianissississimo").value == -40
    assert Dynamic.from_name("pianississimo").value == -30
    assert Dynamic.from_name("pianissimo").value == -20
    assert Dynamic.from_name("piano").value == -10
    assert Dynamic.from_name("mezzo-piano").value == -5
    assert Dynamic.from_name("mezzo-forte").value == 5
    assert Dynamic.from_name("forte").value == 10
    assert Dynamic.from_name("fortissimo").value == 20
    assert Dynamic.from_name("fortississimo").value == 30
    assert Dynamic.from_name("fortissississimo").value == 40

    for name in (
        "pianiss",
        "pianimo",
        "mezzo-pianissimo",
        "mezzo-",
        "mezzo",
        "mezzo-fortissimo",
        "fortimo",
        "fortiss",
        "very loud",
    ):
        with pytest.raises(ValueError):
            Dynamic.from_name(name)

    assert Dynamic.from_symbol("pppp").value == -40
    assert Dynamic.from_symbol("ppp").value == -30
    assert Dynamic.from_symbol("pp").value == -20
    assert Dynamic.from_symbol("p").value == -10
    assert Dynamic.from_symbol("mp").value == -5
    assert Dynamic.from_symbol("mf").value == 5
    assert Dynamic.from_symbol("f").value == 10
    assert Dynamic.from_symbol("ff").value == 20
    assert Dynamic.from_symbol("fff").value == 30
    assert Dynamic.from_symbol("ffff").value == 40

    assert Dynamic.from_symbol("p") < Dynamic.from_symbol("f")
    assert Dynamic.from_symbol("pp") < Dynamic.from_symbol("p")
    assert not (Dynamic.from_symbol("p") < Dynamic.from_symbol("p"))
    assert not (Dynamic.from_symbol("f") < Dynamic.from_symbol("p"))
    assert not (Dynamic.from_symbol("p") < Dynamic.from_symbol("pp"))

    assert Dynamic.from_symbol("p") <= Dynamic.from_symbol("f")
    assert Dynamic.from_symbol("pp") <= Dynamic.from_symbol("p")
    assert Dynamic.from_symbol("p") <= Dynamic.from_symbol("p")
    assert not (Dynamic.from_symbol("f") <= Dynamic.from_symbol("p"))
    assert not (Dynamic.from_symbol("p") <= Dynamic.from_symbol("pp"))

    assert not (Dynamic.from_symbol("p") > Dynamic.from_symbol("f"))
    assert not (Dynamic.from_symbol("pp") > Dynamic.from_symbol("p"))
    assert not (Dynamic.from_symbol("p") > Dynamic.from_symbol("p"))
    assert Dynamic.from_symbol("f") > Dynamic.from_symbol("p")
    assert Dynamic.from_symbol("p") > Dynamic.from_symbol("pp")

    assert not (Dynamic.from_symbol("p") >= Dynamic.from_symbol("f"))
    assert not (Dynamic.from_symbol("pp") >= Dynamic.from_symbol("p"))
    assert Dynamic.from_symbol("p") >= Dynamic.from_symbol("p")
    assert Dynamic.from_symbol("f") >= Dynamic.from_symbol("p")
    assert Dynamic.from_symbol("p") >= Dynamic.from_symbol("pp")

    for symbol in ("mpp", "fp", "mff", "forte", "fm", "n"):
        with pytest.raises(ValueError):
            Dynamic.from_symbol(symbol)

    with pytest.raises(TypeError):
        Dynamic.from_symbol("p") < 5


def test_note():
    from blooper.notes import Accent, Dynamic, Note
    from blooper.pitch import Pitch

    pitch = Pitch(4, "A")

    half_note = Fraction(1, 2)
    quarter_note = Fraction(1, 4)
    eighth_note = Fraction(1, 8)

    # no accent and Accent.Accent means 3/4 length (kind of)
    for accent in (None, Accent.ACCENT):
        for dynamic in (None, Dynamic.from_symbol("f")):
            assert Note.new(half_note, pitch, dynamic, accent=accent).components(
                quarter_note
            ) == (Fraction(7, 16), pitch, dynamic, accent)
            assert Note.new(quarter_note, pitch, dynamic, accent=accent).components(
                quarter_note
            ) == (Fraction(3, 16), pitch, dynamic, accent)
            assert Note.new(eighth_note, pitch, dynamic, accent=accent).components(
                quarter_note
            ) == (Fraction(3, 32), pitch, dynamic, accent)

    # MARCATO is STACCATO + ACCENT
    assert Note.new(half_note, pitch, accent=Accent.MARCATO).components(
        quarter_note
    ) == (
        Fraction(1, 4),
        pitch,
        None,
        Accent.ACCENT,
    )
    assert Note.new(quarter_note, pitch, accent=Accent.MARCATO).components(
        quarter_note
    ) == (Fraction(1, 8), pitch, None, Accent.ACCENT)
    assert Note.new(eighth_note, pitch, accent=Accent.MARCATO).components(
        quarter_note
    ) == (
        Fraction(1, 16),
        pitch,
        None,
        Accent.ACCENT,
    )

    assert Note.new(half_note, pitch, accent=Accent.STACCATO).components(
        quarter_note
    ) == (
        Fraction(1, 4),
        pitch,
        None,
        None,
    )
    assert Note.new(quarter_note, pitch, accent=Accent.STACCATO).components(
        quarter_note
    ) == (Fraction(1, 8), pitch, None, None)
    assert Note.new(eighth_note, pitch, accent=Accent.STACCATO).components(
        quarter_note
    ) == (Fraction(1, 16), pitch, None, None)

    assert Note.new(half_note, pitch, accent=Accent.STACCATISSIMO).components(
        quarter_note
    ) == (Fraction(1, 8), pitch, None, None)
    assert Note.new(quarter_note, pitch, accent=Accent.STACCATISSIMO).components(
        quarter_note
    ) == (Fraction(1, 16), pitch, None, None)
    assert Note.new(eighth_note, pitch, accent=Accent.STACCATISSIMO).components(
        quarter_note
    ) == (Fraction(1, 32), pitch, None, None)

    assert Note.new(half_note, pitch, accent=Accent.TENUTO).components(
        quarter_note
    ) == (
        half_note,
        pitch,
        None,
        None,
    )
    assert Note.new(quarter_note, pitch, accent=Accent.TENUTO).components(
        quarter_note
    ) == (
        quarter_note,
        pitch,
        None,
        None,
    )
    assert Note.new(eighth_note, pitch, accent=Accent.TENUTO).components(
        quarter_note
    ) == (
        eighth_note,
        pitch,
        None,
        None,
    )

    assert Note.new(half_note, pitch, accent=Accent.SLUR).components(quarter_note) == (
        half_note,
        pitch,
        None,
        Accent.SLUR,
    )
    assert Note.new(quarter_note, pitch, accent=Accent.SLUR).components(
        quarter_note
    ) == (
        quarter_note,
        pitch,
        None,
        Accent.SLUR,
    )
    assert Note.new(eighth_note, pitch, accent=Accent.SLUR).components(
        quarter_note
    ) == (
        eighth_note,
        pitch,
        None,
        Accent.SLUR,
    )

    # different beat size
    assert Note.new(half_note, pitch).components(eighth_note) == (
        Fraction(15, 32),
        pitch,
        None,
        None,
    )
    assert Note.new(quarter_note, pitch).components(eighth_note) == (
        Fraction(7, 32),
        pitch,
        None,
        None,
    )
    assert Note.new(eighth_note, pitch).components(eighth_note) == (
        Fraction(3, 32),
        pitch,
        None,
        None,
    )

    assert Note.new(half_note, pitch, accent=Accent.MARCATO).components(
        eighth_note
    ) == (
        Fraction(1, 4),
        pitch,
        None,
        Accent.ACCENT,
    )
    assert Note.new(quarter_note, pitch, accent=Accent.MARCATO).components(
        eighth_note
    ) == (
        Fraction(1, 8),
        pitch,
        None,
        Accent.ACCENT,
    )
    assert Note.new(eighth_note, pitch, accent=Accent.MARCATO).components(
        eighth_note
    ) == (
        Fraction(1, 16),
        pitch,
        None,
        Accent.ACCENT,
    )

    # different drop-off
    assert Note.new(half_note, pitch).components(
        quarter_note, tailoff_factor=Fraction(3, 16)
    ) == (Fraction(29, 64), pitch, None, None)
    assert Note.new(quarter_note, pitch).components(
        quarter_note, tailoff_factor=Fraction(3, 16)
    ) == (Fraction(13, 64), pitch, None, None)
    assert Note.new(eighth_note, pitch).components(
        quarter_note, tailoff_factor=Fraction(3, 16)
    ) == (Fraction(13, 128), pitch, None, None)

    # 0 drop-off
    assert Note.new(half_note, pitch).components(
        quarter_note, tailoff_factor=Fraction(0, 1)
    ) == (half_note, pitch, None, None)
    assert Note.new(quarter_note, pitch).components(
        quarter_note, tailoff_factor=Fraction(0, 1)
    ) == (quarter_note, pitch, None, None)
    assert Note.new(eighth_note, pitch).components(
        quarter_note, tailoff_factor=Fraction(0, 1)
    ) == (eighth_note, pitch, None, None)


def test_grace():
    from blooper.notes import Grace, Note, Tone
    from blooper.pitch import Chord, Pitch

    for grace_pitch in (Pitch(4, "A"), Chord(Pitch(4, "A"), Pitch(3, "A"))):
        for note_pitch in (Pitch(3, "A"), Chord(Pitch(3, "A"), Pitch(2, "A"))):
            grace_tone = Tone(grace_pitch)
            note_tone = Tone(note_pitch)

            for note in (note_pitch, note_tone):
                grace = Grace(grace_pitch, note)
                assert grace.concurrence == max(
                    grace_tone.concurrence, note_tone.concurrence
                )
                assert grace.count() == 1
                for fraction in (Fraction(1, 4), Fraction(1, 2), Fraction(2, 3)):
                    assert grace.duration(fraction) == fraction
                    assert list(grace.notes(fraction)) == [
                        Note(fraction / 4, grace_tone),
                        Note(3 * fraction / 4, note_tone),
                    ]

    grace = Grace(
        Pitch(4, "A"),
        Note(Fraction(1, 4), Tone(Pitch(3, "B"))),
        divisor=8,
    )
    assert grace.concurrence == 1
    assert grace.count() == 1
    for divisor in (2, 4, 8):
        assert grace.duration(Fraction(1, divisor)) == Fraction(1, 4)

    for divisor in (2, 4):
        assert list(grace.notes(Fraction(1, divisor))) == [
            Note(Fraction(1, 32), Tone(Pitch(4, "A"))),
            Note(Fraction(7, 32), Tone(Pitch(3, "B"))),
        ]

    assert list(grace.notes(Fraction(1, 8))) == [
        Note(Fraction(1, 64), Tone(Pitch(4, "A"))),
        Note(Fraction(15, 64), Tone(Pitch(3, "B"))),
    ]

    assert Grace(Pitch(4, "A"), Pitch(4, "B")) == Grace(
        Pitch(4, "A"), Tone(Pitch(4, "B"))
    )
    assert Grace(Pitch(4, "A"), Pitch(4, "B")) != Grace(
        Pitch(4, "A"), Pitch(4, "B"), divisor=8
    )
    # NotImplemented test :/
    assert Grace(Pitch(4, "A"), Pitch(4, "B")) != Pitch(4, "A")

    assert repr(Grace(Pitch(4, "A"), Pitch(4, "B"))) == repr(
        Grace(Pitch(4, "A"), Tone(Pitch(4, "B")))
    )


def test_tuple():
    from blooper.notes import Grace, Note, Rest, Tone, Triplet, Tuplet
    from blooper.pitch import Chord, Pitch

    pentuplet = Tuplet(
        Pitch(4, "A"),
        Chord(Pitch(4, "A"), Pitch(4, "B")),
        Tone(Pitch(4, "A")),
        Grace(Pitch(4, "A"), Pitch(4, "A")),
        Triplet(
            None,
            Pitch(4, "A"),
            Grace(Pitch(4, "A"), Pitch(4, "A")),
        ),
    )
    assert pentuplet.concurrence == 2
    assert pentuplet.count() == 5
    assert pentuplet.duration(Fraction(1, 4)) == Fraction(1, 4)
    assert pentuplet.duration(Fraction(1, 8)) == Fraction(1, 8)

    assert list(pentuplet.notes(Fraction(1, 4))) == [
        Note(Fraction(1, 20), Tone(Pitch(4, "A"))),
        Note(Fraction(1, 20), Tone(Chord(Pitch(4, "A"), Pitch(4, "B")))),
        Note(Fraction(1, 20), Tone(Pitch(4, "A"))),
        Note(Fraction(1, 80), Tone(Pitch(4, "A"))),
        Note(Fraction(3, 80), Tone(Pitch(4, "A"))),
        Rest(Fraction(1, 60)),
        Note(Fraction(1, 60), Tone(Pitch(4, "A"))),
        Note(Fraction(1, 240), Tone(Pitch(4, "A"))),
        Note(Fraction(3, 240), Tone(Pitch(4, "A"))),
    ]

    assert list(pentuplet.notes(Fraction(1, 8))) == [
        Note(Fraction(1, 40), Tone(Pitch(4, "A"))),
        Note(Fraction(1, 40), Tone(Chord(Pitch(4, "A"), Pitch(4, "B")))),
        Note(Fraction(1, 40), Tone(Pitch(4, "A"))),
        Note(Fraction(1, 160), Tone(Pitch(4, "A"))),
        Note(Fraction(3, 160), Tone(Pitch(4, "A"))),
        Rest(Fraction(1, 120)),
        Note(Fraction(1, 120), Tone(Pitch(4, "A"))),
        Note(Fraction(1, 480), Tone(Pitch(4, "A"))),
        Note(Fraction(3, 480), Tone(Pitch(4, "A"))),
    ]

    with pytest.raises(ValueError):
        Tuplet()

    with pytest.raises(ValueError):
        Tuplet(Pitch(4, "A"))

    assert Tuplet(Tone(Pitch(4, "A")), Pitch(4, "A"), Chord(Pitch(4, "A"))) == Triplet(
        Pitch(4, "A"), Chord(Pitch(4, "A")), Tone(Pitch(4, "A"))
    )
    assert Tuplet(Pitch(4, "A"), Pitch(4, "A"), Pitch(4, "A")) != Tuplet(
        Pitch(4, "A"), Pitch(4, "A"), Pitch(4, "A"), Pitch(4, "A")
    )
    assert Tuplet(Pitch(4, "A"), Pitch(4, "A"), Pitch(4, "A")) != Triplet(
        Pitch(4, "A"), Pitch(4, "A"), Pitch(4, "B")
    )
    # NotImplemented
    assert Tuplet(Pitch(4, "A"), Pitch(4, "A"), Pitch(4, "A")) != Pitch(4, "A")
