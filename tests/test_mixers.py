from dataclasses import dataclass
from fractions import Fraction

import pytest


def test_mixer():
    from blooper.instruments import Synthesizer
    from blooper.mixers import Mixer
    from blooper.notes import Dynamic, Rest
    from blooper.parts import Part, Tempo, TimeSignature
    from blooper.pitch import Pitch, Tuning

    tuning = Tuning(Pitch(0, "A"), 10)
    part = Part(
        TimeSignature(4, 4),
        Tempo.ALLEGRO_MODERATO,
        Dynamic.from_name("fortissimo"),
        [[Rest(Fraction(1, 1))]],
    )
    part2 = Part(
        TimeSignature(4, 4),
        Tempo.GRAVE,
        Dynamic.from_name("piano"),
        [[Rest(Fraction(1, 2)), Rest(Fraction(1, 2))]],
    )

    synthesizer = Synthesizer(tuning=tuning)
    square = Synthesizer("square", tuning=tuning)

    assert Mixer.solo(synthesizer, part) == Mixer((synthesizer,), (part,), (1,))
    assert Mixer.solo(synthesizer, part, 0.5) == Mixer((synthesizer,), (part,), (0.5,))

    assert Mixer.even((synthesizer, part)) == Mixer((synthesizer,), (part,), (1,))
    assert Mixer.even((synthesizer, part), (square, part2)) == Mixer(
        (synthesizer, square), (part, part2), (0.5, 0.5)
    )
    assert Mixer.even((synthesizer, part), (square, part2), volume=1.2) == Mixer(
        (synthesizer, square), (part, part2), (0.6, 0.6)
    )

    with pytest.raises(ValueError):
        Mixer.even()

    # Good news, I remembered about mocking just in time to test mixing
    @dataclass
    class FakeInstrument:
        part: list[tuple[int, ...]]
        sample_rate: int

        def play(self, part, sample_rate, channels=2):
            assert sample_rate == self.sample_rate
            yield from self.part

    assert list(
        Mixer.solo(
            FakeInstrument([(0.5, 0.5), (1, 1), (0, 0), (-0.25, -0.25)], 1000), part
        ).mix(1000, 2, 100)
    ) == [(50, 50), (100, 100), (0, 0), (-25, -25)]

    # bounding and make sure samples are being read separately
    assert list(
        Mixer.solo(
            FakeInstrument([(0.5, -1.1), (1.2, -1), (0, 0), (-0.25, 0.25)], 1000), part
        ).mix(1000, 2, 100)
    ) == [(50, -100), (100, -100), (0, 0), (-25, 25)]

    # combining samples
    assert (
        list(
            Mixer.even(
                (
                    FakeInstrument(
                        [(0.5, -1.1), (1.2, -1), (0, 0), (-0.25, 0.25)], 1000
                    ),
                    part,
                ),
                (
                    FakeInstrument(
                        [(0.1, -0.1), (-1.3, -1), (0, 0.5), (-0.5, 0.85)], 1000
                    ),
                    part,
                ),
                volume=2,
            ).mix(1000, 2, 100)
        )
    ) == [(60, -100), (-10, -100), (0, 50), (-75, 100)]

    # parts with different lengths
    assert (
        list(
            Mixer.even(
                (FakeInstrument([(0.5, -1.1), (1.2, -1)], 1000), part),
                (
                    FakeInstrument(
                        [(0.1, -0.1), (-1.3, -1), (0, 0.5), (-0.5, 0.85)], 1000
                    ),
                    part,
                ),
            ).mix(1000, 2, 100)
        )
    ) == [(30, -60), (-5, -100), (0, 25), (-25, 42)]
