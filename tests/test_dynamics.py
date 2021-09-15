from fractions import Fraction

import pytest


def test_dynamic_range():
    from blooper.dynamics import DynamicRange
    from blooper.notes import Dynamic

    one_volume = DynamicRange(minimum_output=1, full_output=1, maximum_output=1)

    assert one_volume.volume(Dynamic.from_symbol("ppp")) == 1
    assert one_volume.volume(Dynamic.from_symbol("pp")) == 1
    assert one_volume.volume(Dynamic.from_symbol("p")) == 1
    assert one_volume.volume(Dynamic.from_symbol("mp")) == 1
    # the mythical mezzo-mezzo
    assert one_volume.volume(Dynamic(0)) == 1
    assert one_volume.volume(Dynamic.from_symbol("mf")) == 1
    assert one_volume.volume(Dynamic.from_symbol("f")) == 1
    assert one_volume.volume(Dynamic.from_symbol("ff")) == 1
    assert one_volume.volume(Dynamic.from_symbol("fff")) == 1
    assert one_volume.volume(Dynamic.from_symbol("ffff")) == 1
    assert one_volume.volume(Dynamic.from_symbol("fffff")) == 1

    dynamic = DynamicRange(
        minimum=Dynamic.from_symbol("pp"),
        full=Dynamic.from_symbol("ff"),
        maximum=Dynamic.from_symbol("ffff"),
        minimum_output=0.2,
        full_output=1,
        maximum_output=1.2,
    )

    assert dynamic.volume(Dynamic.from_symbol("ppp")) == 0.2
    assert dynamic.volume(Dynamic.from_symbol("pp")) == 0.2
    assert dynamic.volume(Dynamic.from_symbol("p")) == 0.4
    # reminder, we currently offset mp/mf so they're one step away from
    # eachother but half a step from p/f. That these numbers all line
    # up so cleanly was an accident but they do which is clearly fate.
    # or I'll find out these numbers don't sound right and I'll regret
    # this comment. Guess we'll find out.
    assert dynamic.volume(Dynamic.from_symbol("mp")) == 0.5
    # love to do math on a computer
    assert round(dynamic.volume(Dynamic(0)), 14) == 0.6
    assert dynamic.volume(Dynamic.from_symbol("mf")) == 0.7
    assert dynamic.volume(Dynamic.from_symbol("f")) == 0.8
    assert dynamic.volume(Dynamic.from_symbol("ff")) == 1
    assert dynamic.volume(Dynamic.from_symbol("fff")) == 1.1
    assert dynamic.volume(Dynamic.from_symbol("ffff")) == 1.2
    assert dynamic.volume(Dynamic.from_symbol("fffff")) == 1.2

    # full can't be smaller than minimum
    with pytest.raises(ValueError):
        DynamicRange(
            minimum=Dynamic.from_symbol("f"),
            full=Dynamic.from_symbol("mf"),
            maximum=Dynamic.from_symbol("ff"),
        )

    with pytest.raises(ValueError):
        DynamicRange(minimum_output=1, full_output=0.5, maximum_output=1.2)

    # full can't be smaller than minimum
    with pytest.raises(ValueError):
        DynamicRange(
            minimum=Dynamic.from_symbol("p"),
            full=Dynamic.from_symbol("f"),
            maximum=Dynamic.from_symbol("mf"),
        )

    with pytest.raises(ValueError):
        DynamicRange(minimum_output=0.5, full_output=1.2, maximum_output=1)

    # if dynamic matches, volume must
    with pytest.raises(ValueError):
        DynamicRange(
            minimum=Dynamic.from_symbol("ff"),
            full=Dynamic.from_symbol("ff"),
            maximum=Dynamic.from_symbol("ffff"),
            minimum_output=0.5,
            full_output=1,
            maximum_output=1.2,
        )

    with pytest.raises(ValueError):
        DynamicRange(
            minimum=Dynamic.from_symbol("pp"),
            full=Dynamic.from_symbol("ff"),
            maximum=Dynamic.from_symbol("ff"),
            minimum_output=0.5,
            full_output=1,
            maximum_output=1.2,
        )

    # At some point, you're just writing bullshit tests to improve
    # coverage and you should ask yourself if you're really gaining
    # anything
    assert DynamicRange() == DynamicRange()
    assert DynamicRange(full=Dynamic.from_symbol("ff")) == DynamicRange(
        full=Dynamic.from_symbol("ff")
    )
    assert DynamicRange(full=Dynamic.from_symbol("fff")) != DynamicRange(
        full=Dynamic.from_symbol("ff")
    )
    assert DynamicRange() != Dynamic.from_symbol("f")


def test_homogenous():
    from blooper.dynamics import DynamicRange, Homogenous
    from blooper.notes import Accent, Dynamic, Tone
    from blooper.pitch import Pitch

    dynamics = DynamicRange()
    envelope = Homogenous(dynamics)

    for symbol in ("ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"):
        for accent in (None, Accent.ACCENT, Accent.SLUR):
            dynamic = Dynamic.from_symbol(symbol)
            tone = Tone(100, Pitch(4, "A"), dynamic, accent=accent)

            for start in (0, 0.5, 1):
                volumes = list(envelope.volumes(tone, 100, start))

                assert volumes == 100 * [dynamics.volume(dynamic)]


def test_adsr_rates():
    from blooper.dynamics import AttackDecaySustainRelease, DynamicRange
    from blooper.notes import Accent, Dynamic, Tone
    from blooper.pitch import Pitch

    dynamics = DynamicRange()
    forte = Dynamic.from_symbol("f")
    pitch = Pitch(4, "A")

    # quick checks on automatic settings
    envelope = AttackDecaySustainRelease(dynamics, attack=0.1, decay=None, release=None)
    assert envelope.attack == 0.1
    assert envelope.decay == 0.1
    assert envelope.release == 0.1

    envelope = AttackDecaySustainRelease(dynamics, attack=0.1, decay=None, release=0.05)
    assert envelope.attack == 0.1
    assert envelope.decay == 0.1
    assert envelope.release == 0.05

    envelope = AttackDecaySustainRelease(dynamics, attack=0.1, decay=0.2, release=None)
    assert envelope.attack == 0.1
    assert envelope.decay == 0.2
    assert envelope.release == 0.2

    envelope = AttackDecaySustainRelease(dynamics, attack=0.1, decay=0.2, release=0.05)
    assert envelope.attack == 0.1
    assert envelope.decay == 0.2
    assert envelope.release == 0.05

    # just making sure this doesn't error
    AttackDecaySustainRelease(dynamics, sustain_level=1)

    # what about bad values
    with pytest.raises(ValueError):
        AttackDecaySustainRelease(dynamics, sustain_level=1.1)

    for parameter in ("attack", "decay", "release"):
        for value in (0, -0.1):
            with pytest.raises(ValueError):
                AttackDecaySustainRelease(dynamics, **{parameter: value})

    # ok, let's actually test rates
    envelope = AttackDecaySustainRelease(
        dynamics,
        attack=0.1,
        decay=0.05,
        release=0.2,
        sustain_level=0.9,
        accent_multiplier=1.1,
        accent_peak=Fraction(1, 2),
        accent_sustain_level=0.7,
    )

    # no accent, easy
    peak, sustain, end, attack_rate, decay_rate, release_rate = envelope._rates(
        Tone(1_000, pitch, forte), 500
    )
    assert peak == dynamics.volume(forte)
    assert sustain == peak * 0.9
    assert end == 0
    assert attack_rate == 1 / (500 * 0.1)
    assert decay_rate == 1 / (500 * 0.05)
    assert release_rate == 1 / (500 * 0.2)

    # different sample rate
    peak, sustain, end, attack_rate, decay_rate, release_rate = envelope._rates(
        Tone(1_000, pitch, forte), 5_000
    )
    assert peak == dynamics.volume(forte)
    assert sustain == peak * 0.9
    assert end == 0
    assert attack_rate == 1 / (5_000 * 0.1)
    assert decay_rate == 1 / (5_000 * 0.05)
    assert release_rate == 1 / (5_000 * 0.2)

    # accented, peak should be higher and rates will be quicker
    peak, sustain, end, attack_rate, decay_rate, release_rate = envelope._rates(
        Tone(1_000, pitch, forte, Accent.ACCENT), 500
    )
    assert peak == dynamics.volume(Dynamic(forte.value + round(forte.step / 2)))
    assert sustain == dynamics.volume(forte) * 0.9
    assert end == 0
    assert attack_rate == 1 / (500 * 0.1 / 1.1)
    assert decay_rate == 1 / (500 * 0.05 / 1.1)
    assert release_rate == 1 / (500 * 0.2 / 1.1)

    # slured. end should be sustain
    peak, sustain, end, attack_rate, decay_rate, release_rate = envelope._rates(
        Tone(1_000, pitch, forte, Accent.SLUR), 500
    )
    assert peak == dynamics.volume(forte)
    assert sustain == peak * 0.9
    assert end == sustain
    assert attack_rate == 1 / (500 * 0.1)
    assert decay_rate == 1 / (500 * 0.05)
    assert release_rate == 1 / (500 * 0.2)


def test_adsr_volumes():
    from blooper.dynamics import AttackDecaySustainRelease, DynamicRange
    from blooper.notes import Dynamic, Tone
    from blooper.pitch import Pitch

    def volumes_list(*args):
        return [round(value, 14) for value in AttackDecaySustainRelease._volumes(*args)]

    # no note? don't play it
    assert volumes_list(0, 0, 1, 0.8, 0, 0.1, 0.2, 0.05) == []

    # if end is higher doesn't mean you have to go to it
    # TODO: or does it. hmmm
    assert volumes_list(0, 0, 1, 0.8, 0.1, 0.1, 0.2, 0.05) == []

    # need to get back to 0 no matter what
    assert volumes_list(0, 0.6, 1, 0.8, 0.1, 0.1, 0.2, 0.05) == [
        0.55,
        0.5,
        0.45,
        0.4,
        0.35,
        0.3,
        0.25,
        0.2,
        0.15,
        0.1,
        0.05,
        0,
    ]

    # what if it takes less than a sample
    assert volumes_list(0, 0.03, 1, 0.8, 0.1, 0.1, 0.2, 0.05) == [0]

    # only sustain/release
    assert volumes_list(5, 1, 1, 1, 0, 0.1, 0.2, 0.5) == [
        1,
        1,
        1,
        0.5,
        0,
    ]

    # only time to attack/release (so below sustain)
    assert volumes_list(10, 0.0, 1, 0.8, 0.1, 0.1, 0.2, 0.05) == [
        0.1,
        0.2,
        0.3,
        0.4,
        0.35,
        0.3,
        0.25,
        0.2,
        0.15,
        0.1,
        0.05,
        0.0,
    ]

    # above sustain but release is faster
    assert volumes_list(10, 0.0, 1, 0.3, 0.1, 0.1, 0.02, 0.05) == [
        0.1,
        0.2,
        0.3,
        0.4,
        0.35,
        0.3,
        0.25,
        0.2,
        0.15,
        0.1,
        0.05,
        0.0,
    ]

    # attack, decay, release
    assert volumes_list(15, 0.0, 1, 0.3, 0, 0.1, 0.2, 0.05) == [
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.5,
        0.3,
        0.25,
        0.2,
        0.15,
        0.1,
        0.05,
        0.0,
    ]

    # decay, release
    assert volumes_list(10, 1, 1, 0.4, 0.05, 0.1, 0.2, 0.05) == [
        0.8,
        0.6,
        0.4,
        0.35,
        0.3,
        0.25,
        0.2,
        0.15,
        0.1,
        0.05,
        0.0,
    ]

    # decay, sustain, release
    assert volumes_list(15, 1, 1, 0.4, 0.05, 0.1, 0.2, 0.05) == [
        0.8,
        0.6,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.35,
        0.3,
        0.25,
        0.2,
        0.15,
        0.1,
        0.05,
        0.0,
    ]

    # ADSR!
    assert volumes_list(25, 0, 1, 0.4, 0.05, 0.1, 0.2, 0.05) == [
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.9,
        1.0,
        0.8,
        0.6,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.35,
        0.3,
        0.25,
        0.2,
        0.15,
        0.1,
        0.05,
        0.0,
    ]

    # ADSR, would go above
    assert volumes_list(25, 0, 1, 0.4, 0.05, 0.1, 0.2, 0.2) == [
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.9,
        1.0,
        0.8,
        0.6,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.2,
        0.0,
    ]

    # ASR
    assert volumes_list(20, 0, 1, 1, 0.05, 0.1, 0.2, 0.2) == [
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.9,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        0.8,
        0.6,
        0.4,
        0.2,
        0.0,
    ]

    # Attack Decay
    assert volumes_list(20, 0, 1, 0, 0, 0.1, 0.2, 0.1) == [
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.9,
        1.0,
        0.8,
        0.6,
        0.4,
        0.2,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]

    # Decay
    assert volumes_list(10, 1, 1, 0, 0, 0.1, 0.2, 0.1) == [
        0.8,
        0.6,
        0.4,
        0.2,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]

    # padded (this should be impossible)
    assert volumes_list(10, 0.8, 0.8, 1.0, 0, 0.1, 0.05, 0.2) == [
        0.6,
        0.4,
        0.2,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]

    # lock decay to sustain
    assert volumes_list(10, 1, 1, 0.75, 0, 0.1, 0.1, 0.2) == [
        0.9,
        0.8,
        0.75,
        0.75,
        0.75,
        0.75,
        0.55,
        0.35,
        0.15,
        0.0,
    ]

    # Ok, one bad test putting it all together I guess :/
    forte = Dynamic.from_symbol("f")
    dynamics = DynamicRange(full=forte)
    pitch = Pitch(4, "A")

    # quick checks on automatic settings
    envelope = AttackDecaySustainRelease(
        dynamics,
        attack=0.4,
        decay=0.8,
        release=0.2,
        sustain_level=0.8,
    )

    volumes = [
        round(value, 14) for value in envelope.volumes(Tone(10, pitch, forte), 5)
    ]
    assert volumes == [0.5, 1, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0]

    # and yet, here we are writing bullshit tests for coverage
    assert AttackDecaySustainRelease(dynamics) == AttackDecaySustainRelease(dynamics)
    assert AttackDecaySustainRelease(dynamics, attack=0.3) != AttackDecaySustainRelease(
        dynamics, attack=0.4
    )
    assert AttackDecaySustainRelease(dynamics, attack=0.3) != dynamics
