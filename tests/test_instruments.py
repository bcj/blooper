import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator

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


def test_stereo_to_mono():
    from blooper.instruments import Instrument

    assert Instrument.stereo_to_mono(1, 1, 0) == (1,)
    assert Instrument.stereo_to_mono(0.5, 0.5, 0) == (0.5,)
    assert Instrument.stereo_to_mono(0.75, 0.25, 0) == (0.5,)
    assert Instrument.stereo_to_mono(0, 0, 0) == (0,)

    assert Instrument.stereo_to_mono(1, 0, -1) == (1,)
    assert Instrument.stereo_to_mono(0, 1, -1) == (0,)
    assert Instrument.stereo_to_mono(0.5, 0, -1) == (0.5,)
    assert Instrument.stereo_to_mono(0, 0, -1) == (0,)

    assert Instrument.stereo_to_mono(1, 0, 1) == (0,)
    assert Instrument.stereo_to_mono(0, 1, 1) == (1,)
    assert Instrument.stereo_to_mono(0, 0.5, 1) == (0.5,)
    assert Instrument.stereo_to_mono(0, 0, 1) == (0,)

    assert Instrument.stereo_to_mono(0.25, 0.75, 0.5) == (0.625,)
    assert Instrument.stereo_to_mono(0.75, 0.25, 0.5) == (0.375,)
    assert Instrument.stereo_to_mono(0, 0, 0.5) == (0,)


def test_synthesizer():
    from blooper.dynamics import AttackDecaySustainRelease, DynamicRange, Homogenous
    from blooper.instruments import Synthesizer
    from blooper.notes import Accent, Dynamic, Note, Rest
    from blooper.parts import Part, Tempo, TimeSignature
    from blooper.pitch import Pitch, Tuning

    tuning = Tuning(Pitch(0, "A"), 10)
    part = Part(
        TimeSignature.new(4, 4),
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
        TimeSignature.new(2, 4),
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


def test_sampler():
    from blooper.dynamics import DynamicRange, Homogenous
    from blooper.filetypes import UsageMetadata
    from blooper.instruments import Sampler
    from blooper.notes import Dynamic, Tone
    from blooper.pitch import Pitch, Tuning
    from blooper.wavs import WavSample, record

    # helpers
    @dataclass
    class FakeMixer:
        part: list[tuple[float, ...]]

        def mix(
            self, sample_rate: int, channels: int, max_value: int
        ) -> Iterator[tuple[int, ...]]:
            for sample_set in self.part:
                yield tuple(int(sample * max_value) for sample in sample_set)

    def write_wav(path: Path, sample_rate: int, samples: list[tuple[int, ...]]):
        if samples:
            channels = len(samples[0])
        else:
            channels = 2

        record(path, FakeMixer(samples), channels=channels, sample_rate=sample_rate)

    tuning = Tuning(Pitch(4, "A"), 400)

    # map samples
    assert Sampler.map_samples({}, "wav") == {}

    with pytest.raises(NotImplementedError):
        Sampler.map_samples({}, "mp3")

    with TemporaryDirectory() as directory_name:
        directory = Path(directory_name)

        sample_paths = {}

        for name, frequency, sample_rate in (
            ("a4_20,000.wav", 400, 20_000),
            ("a4_20,000b.wav", 400, 20_000),
            ("a4_40,000.wav", 400, 40_000),
            ("a3_20,000.wav", 200, 20_000),
            ("a3_20,000b.wav", 200, 20_000),
            ("a3_40,000.wav", 200, 40_000),
        ):
            path = directory / name
            write_wav(path, sample_rate, [(0, 0)])
            sample_paths[path] = UsageMetadata(frequency)

        meta200 = UsageMetadata(200)
        meta400 = UsageMetadata(400)
        assert WavSample(directory / "a3_20,000.wav", meta200) == WavSample(
            directory / "a3_20,000.wav", meta200
        )

        expected = {
            20_000: {
                200: {
                    WavSample(directory / "a3_20,000.wav", meta200),
                    WavSample(directory / "a3_20,000b.wav", meta200),
                },
                400: {
                    WavSample(directory / "a4_20,000.wav", meta400),
                    WavSample(directory / "a4_20,000b.wav", meta400),
                },
            },
            40_000: {
                200: {WavSample(directory / "a3_40,000.wav", meta200)},
                400: {WavSample(directory / "a4_40,000.wav", meta400)},
            },
        }
        assert Sampler.map_samples(sample_paths, "wav") == expected

        # constructor
        config = directory / "samples.json"

        with config.open("w") as stream:
            json.dump({"format": "wav", "samples": []}, stream)

        sampler = Sampler.from_file(config, tuning)
        assert sampler.samples == {}

        with config.open("w") as stream:
            json.dump(
                {
                    "format": "wav",
                    "samples": [
                        {"path": "a4_20,000.wav", "frequency": 400},
                        {
                            "path": str(directory / "a4_20,000b.wav"),
                            "frequency": 400,
                        },
                        {"path": "a4_40,000.wav", "frequency": 400},
                        {"path": "a3_20,000.wav", "frequency": 200},
                        {
                            "path": str(directory / "a3_20,000b.wav"),
                            "frequency": 200,
                            "min-volume": "pp",
                            "maximum-volume": "forte",
                        },
                        {
                            "path": "a3_40,000.wav",
                            "frequency": 200,
                            "minimum-volume": "pianissimo",
                            "max-volume": "f",
                        },
                    ],
                },
                stream,
            )

        pianissimo = Dynamic.from_symbol("pp")
        forte = Dynamic.from_symbol("f")
        meta200ppf = UsageMetadata(200, pianissimo, forte)

        sampler = Sampler.from_file(config, tuning)
        assert sampler.samples == expected

        # compatible_samples

        # matching frequency
        assert sampler.compatible_samples(400, 10_000) == {
            WavSample(directory / "a4_20,000.wav", meta400),
            WavSample(directory / "a4_20,000b.wav", meta400),
            WavSample(directory / "a4_40,000.wav", meta400),
        }
        assert sampler.compatible_samples(400, 20_000) == {
            WavSample(directory / "a4_20,000.wav", meta400),
            WavSample(directory / "a4_20,000b.wav", meta400),
            WavSample(directory / "a4_40,000.wav", meta400),
        }
        assert sampler.compatible_samples(400, 30_000) == set()
        assert sampler.compatible_samples(400, 40_000) == {
            WavSample(directory / "a4_40,000.wav", meta400),
        }

        # out of range
        assert sampler.compatible_samples(300, 10_000) == set()

        # in range
        assert Sampler.from_file(
            config, tuning, max_distance=500  # actual distance is 498
        ).compatible_samples(300, 10_000) == {
            WavSample(directory / "a4_20,000.wav", meta400),
            WavSample(directory / "a4_20,000b.wav", meta400),
            WavSample(directory / "a4_40,000.wav", meta400),
        }

        # wait, why didn't you just pick different samples instead of
        # finding the note equidistant from the samples you already had?
        assert Sampler.from_file(config, tuning, max_distance=600).compatible_samples(
            282.842712474619, 10_000
        ) == {
            WavSample(directory / "a3_20,000.wav", meta200),
            WavSample(directory / "a3_20,000b.wav", meta200ppf),
            WavSample(directory / "a3_40,000.wav", meta200ppf),
            WavSample(directory / "a4_20,000.wav", meta200),
            WavSample(directory / "a4_20,000b.wav", meta200),
            WavSample(directory / "a4_40,000.wav", meta200),
        }

        # filtering on volume
        sampler = Sampler(
            {
                directory / "a3_20,000.wav": UsageMetadata(200, pianissimo, forte),
                directory / "a3_20,000b.wav": UsageMetadata(200, pianissimo),
                directory / "a3_40,000.wav": UsageMetadata(200, forte),
            },
            tuning,
        )
        assert 3 == len(sampler.compatible_samples(200, 20_000))
        assert 2 == len(sampler.compatible_samples(200, 20_000, pianissimo))
        assert 3 == len(sampler.compatible_samples(200, 20_000, forte))
        assert 2 == len(
            sampler.compatible_samples(200, 20_000, Dynamic.from_symbol("ff"))
        )
        assert 0 == len(
            sampler.compatible_samples(200, 20_000, Dynamic.from_symbol("ppp"))
        )

        # play
        paths = {}
        for frequency, samples in (
            (200, [(1,), (-1,), (1,), (-1,), (1,)]),
            (400, [(0.5, 0.5), (-0.5, -0.5)]),
        ):
            path = directory / f"{frequency}.wav"
            write_wav(path, 20_000, samples)
            paths[path] = UsageMetadata(frequency)

        envelope = Homogenous(DynamicRange(minimum_output=1, full_output=1))

        class FakePart:
            def __init__(self, tones):
                self._tones = tones

            def tones(self, sample_rate):
                yield from self._tones

        def compare_samples(a, b, digits=9):
            a = list(a)
            b = list(b)
            assert len(a) == len(b)
            for item_a, item_b in zip(a, b):
                assert [round(channel, digits) for channel in item_a] == [
                    round(channel, digits) for channel in item_b
                ]

        sampler = Sampler(paths, tuning, envelope, loop=False)
        part = FakePart(
            [
                (3, Tone(3, Pitch(3, "A"), Dynamic.from_name("forte"))),
                (7, Tone(3, Pitch(4, "A"), Dynamic.from_name("forte"))),
                (11, Tone(3, Pitch(5, "A"), Dynamic.from_name("forte"))),
                (14, Tone(3, Pitch(4, "A"), Dynamic.from_name("forte"))),
            ]
        )

        # mono, no loop
        compare_samples(
            sampler.play(part, 20_000, channels=1),
            [
                (0,),
                (0,),
                (0,),
                (1,),
                (-1,),
                (1,),
                (0,),
                (0.5,),
                (-0.5,),
                (0,),
                (0,),
                (0,),
                (0,),
                (0,),
                (0.5,),
                (-0.5,),
            ],
        )

        # stereo, no loop
        compare_samples(
            sampler.play(part, 20_000, channels=2),
            [
                (0, 0),
                (0, 0),
                (0, 0),
                (0.5, 0.5),
                (-0.5, -0.5),
                (0.5, 0.5),
                (0, 0),
                (0.5, 0.5),
                (-0.5, -0.5),
                (0, 0),
                (0, 0),
                (0, 0),
                (0, 0),
                (0, 0),
                (0.5, 0.5),
                (-0.5, -0.5),
            ],
        )

        # quadrophenia
        with pytest.raises(NotImplementedError):
            list(sampler.play(part, 20_000, channels=4))

        # mono, loop
        sampler = Sampler(paths, tuning, envelope, loop=True)
        compare_samples(
            sampler.play(part, 20_000, channels=1),
            [
                (0,),
                (0,),
                (0,),
                (1,),
                (-1,),
                (1,),
                (0,),
                (0.5,),
                (-0.5,),
                (0.5,),
                (0,),
                (0,),
                (0,),
                (0,),
                (0.5,),
                (-0.5,),
                (0.5,),
            ],
        )

        # stereo, loop
        compare_samples(
            sampler.play(part, 20_000, channels=2),
            [
                (0, 0),
                (0, 0),
                (0, 0),
                (0.5, 0.5),
                (-0.5, -0.5),
                (0.5, 0.5),
                (0, 0),
                (0.5, 0.5),
                (-0.5, -0.5),
                (0.5, 0.5),
                (0, 0),
                (0, 0),
                (0, 0),
                (0, 0),
                (0.5, 0.5),
                (-0.5, -0.5),
                (0.5, 0.5),
            ],
        )
