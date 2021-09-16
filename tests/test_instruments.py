from fractions import Fraction

import pytest


def test_then_zeroes():
    from blooper.instruments import then_zeroes

    iterable = then_zeroes([])
    assert next(iterable) == 0
    assert next(iterable) == 0
    assert next(iterable) == 0

    iterable = then_zeroes([1, 2, 3])
    assert next(iterable) == 1
    assert next(iterable) == 2
    assert next(iterable) == 3
    assert next(iterable) == 0
    assert next(iterable) == 0
    assert next(iterable) == 0


def test_mono_to_stereo():
    from blooper.instruments import Instrument

    assert Instrument.mono_to_stereo(1, 0) == (0.5, 0.5)
    assert Instrument.mono_to_stereo(0.5, 0) == (0.25, 0.25)
    assert Instrument.mono_to_stereo(0, 0) == (0, 0)

    assert Instrument.mono_to_stereo(1, -1) == (1, 0)
    assert Instrument.mono_to_stereo(0.5, -1) == (0.5, 0)
    assert Instrument.mono_to_stereo(0, -1) == (0, 0)

    assert Instrument.mono_to_stereo(1, 1) == (0, 1)
    assert Instrument.mono_to_stereo(0.5, 1) == (0, 0.5)
    assert Instrument.mono_to_stereo(0, 1) == (0, 0)

    assert Instrument.mono_to_stereo(1, 0.5) == (0.25, 0.75)
    assert Instrument.mono_to_stereo(0.5, 0.5) == (0.125, 0.375)
    assert Instrument.mono_to_stereo(0, 0.5) == (0, 0)


def test_synthesizer():
    from blooper.dynamics import AttackDecaySustainRelease, DynamicRange, Homogenous
    from blooper.instruments import Synthesizer
    from blooper.notes import Accent, Dynamic, Note, Rest
    from blooper.parts import Part, Tempo, TimeSignature
    from blooper.pitch import Pitch, Tuning

    tuning = Tuning(Pitch(0, "A"), 10)
    part = Part(
        TimeSignature(4, 4),
        Tempo.ALLEGRO_MODERATO,
        Dynamic.from_name("fortissimo"),
        [
            [
                Note(Fraction(1, 2), Pitch(0, "A"), accent=Accent.TENUTO),
                Rest(Fraction(1, 4)),
                Note(Fraction(1, 4), Pitch(-1, "A"), accent=Accent.TENUTO),
            ],
        ],
    )

    homogenous = Synthesizer(
        tuning, wave="square", balance=0.5, envelope=Homogenous(DynamicRange())
    )
    assert list(homogenous.play(part, 20)) == [
        (0.25, 0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
    ]

    # double the sample rate, double the samples
    assert list(homogenous.play(part, 40)) == [
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (0.25, 0.75),
    ]

    adsr = Synthesizer(
        tuning,
        wave="square",
        envelope=AttackDecaySustainRelease(
            DynamicRange(), attack=0.1, decay=0.5, release=0.5
        ),
    )
    assert [
        tuple(round(value, 14) for value in sample)
        for sample in adsr.play(part, 20, channels=1)
    ] == [
        (0.5,),
        (-1,),
        (0.9,),
        (-0.8,),
        (0.8,),
        (-0.8,),
        (0.8,),
        (-0.8,),
        (0.8,),
        (-0.8,),
        (0.8,),
        (-0.8,),
        (0.7,),
        (-0.6,),
        (0.5,),
        (-0.4,),
        (0.3,),
        (-0.2,),
        (0.1,),
        (0,),
        (0,),
        (0,),
        (0,),
        (0,),
        (0,),
        (0,),
        (0,),
        (0,),
        (0,),
        (0,),
        (-0.5,),
        (1,),
        (0.7,),
        (-0.6,),
        (-0.5,),
        (0.4,),
        (0.3,),
        (-0.2,),
        (-0.1,),
        (0,),
    ]

    with pytest.raises(NotImplementedError):
        list(adsr.play(part, 20, channels=3))

    part = Part(
        TimeSignature(2, 4),
        Tempo.ALLEGRO_MODERATO,
        Dynamic.from_name("fortissimo"),
        [
            [
                Rest(Fraction(1, 4)),
                Note(Fraction(1, 4), Pitch(-1, "A"), accent=Accent.TENUTO),
            ],
        ],
    )

    assert list(homogenous.play(part, 20)) == [
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
        (-0.25, -0.75),
        (-0.25, -0.75),
        (0.25, 0.75),
        (0.25, 0.75),
    ]

    # TODO: default wave and envelope. This is just defaults checking
    default_envelope = AttackDecaySustainRelease(DynamicRange())

    synthesizer = Synthesizer(tuning, wave=None)
    assert synthesizer.wave == "sine"
    assert synthesizer.envelope == default_envelope

    loud_only = DynamicRange(minimum=Dynamic.from_name("forte"))
    synthesizer = Synthesizer(tuning, wave=None, dynamics=loud_only)
    assert synthesizer.envelope == AttackDecaySustainRelease(loud_only)

    synthesizer = Synthesizer(
        tuning, wave=None, dynamics=loud_only, envelope=default_envelope
    )
    assert synthesizer.envelope == default_envelope
