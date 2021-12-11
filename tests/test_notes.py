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
