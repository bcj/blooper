from fractions import Fraction

import pytest


def test_time_signature():
    from blooper.parts import TimeSignature

    assert TimeSignature.new(4, 4) != TimeSignature.new(1, 1)
    assert str(TimeSignature.new(4, 4)) == "4/4"
    assert str(TimeSignature.new(3, 4)) == "3/4"
    assert str(TimeSignature.new(7, 8)) == "7/8"


def test_measure():
    from blooper.notes import Accent, Dynamic, Grace, Note, Rest
    from blooper.parts import KEYS, Key, Measure, State, Tempo, TimeSignature
    from blooper.pitch import FLAT, NATURAL, SHARP, Chord, Pitch

    assert Measure().notes == []
    assert Measure((Rest(Fraction(x, 4)) for x in range(1, 4))).notes == [
        Rest(Fraction(1, 4)),
        Rest(Fraction(2, 4)),
        Rest(Fraction(3, 4)),
    ]

    piano = Dynamic.from_symbol("p")
    mezzo_forte = Dynamic.from_symbol("mf")
    forte = Dynamic.from_symbol("f")

    # concurrence
    assert Measure().concurrence() == 0
    assert Measure([Rest(Fraction(1, 1))]).concurrence() == 0
    # black, you have bad opinions sometimes
    assert (
        Measure(
            [Rest(Fraction(1, 1)), Note.new(Fraction(1, 1), Pitch(4, "A"))]
        ).concurrence()
        == 1
    )
    assert (
        Measure(
            [
                Rest(Fraction(1, 1)),
                Note.new(Fraction(1, 1), Chord(Pitch(4, "A"), Pitch(4, "B"))),
            ]
        ).concurrence()
        == 2
    )

    # add
    measure = Measure([Note.new(Fraction(1, 4), Pitch(4, "A"))])
    measure.add(Note.new(Fraction(1, 4), Pitch(4, "B")))
    assert measure.notes == [
        Note.new(Fraction(1, 4), Pitch(4, "A")),
        Note.new(Fraction(1, 4), Pitch(4, "B")),
    ]

    # beat_size needs to be supplied if time isn't
    with pytest.raises(ValueError):
        measure.add(
            Note.new(Fraction(1, 8), Pitch(4, "A")),
            key=Key.new("A", True, flats=("A",)),
            tempo=Tempo.LARGHETO,
            dynamic=forte,
            accidentals={"A": FLAT, "C": SHARP},
        )

    measure.add(
        Note.new(Fraction(1, 8), Pitch(4, "A")),
        key=Key.new("A", True, flats=("A",)),
        tempo=Tempo.LARGHETO,
        dynamic=forte,
        accidentals={"A": FLAT, "C": SHARP},
        beat_size=Fraction(1, 4),
    )
    assert measure.notes == [
        Note.new(Fraction(1, 4), Pitch(4, "A")),
        Note.new(Fraction(1, 4), Pitch(4, "B")),
        Note.new(Fraction(1, 8), Pitch(4, "A")),
    ]
    assert measure.keys == {Fraction(1, 2): Key.new("A", True, flats=("A",))}
    assert measure.tempos == {Fraction(1, 2): Tempo.LARGHETO}
    assert measure.dynamics == {Fraction(1, 2): forte}
    assert measure.accidentals == {Fraction(1, 2): {"A": FLAT, "C": SHARP}}

    measure = Measure(
        [Rest(Fraction(1, 4)), Grace(Pitch(4, "A"), Pitch(3, "A"))],
        time=TimeSignature.new(7, 8),
    )
    measure.add(
        Note.new(Fraction(1, 8), Pitch(4, "A")),
        key=Key.new("A", True, flats=("A",)),
        tempo=Tempo.LARGHETO,
        dynamic=forte,
        accidentals={"A": FLAT, "C": SHARP},
    )
    assert measure.notes == [
        Rest(Fraction(1, 4)),
        Grace(Pitch(4, "A"), Pitch(3, "A")),
        Note.new(Fraction(1, 8), Pitch(4, "A")),
    ]
    assert measure.keys == {Fraction(3, 8): Key.new("A", True, flats=("A",))}
    assert measure.tempos == {Fraction(3, 8): Tempo.LARGHETO}
    assert measure.dynamics == {Fraction(3, 8): forte}
    assert measure.accidentals == {Fraction(3, 8): {"A": FLAT, "C": SHARP}}

    # position
    assert Measure._position(TimeSignature.new(4, 4), Fraction(0, 1)) == "0"
    assert Measure._position(TimeSignature.new(4, 4), Fraction(1, 4)) == "1"
    assert Measure._position(TimeSignature.new(4, 4), Fraction(2, 4)) == "2"
    assert Measure._position(TimeSignature.new(4, 4), Fraction(1, 8)) == "0 + 1/8"
    assert Measure._position(TimeSignature.new(4, 4), Fraction(5, 8)) == "2 + 1/8"

    # basic play
    notes = [
        Grace(Pitch(4, "G"), Note.new(Fraction(1, 4), Pitch(4, "A"))),
        Note.new(Fraction(1, 4), Pitch(4, "B"), forte),
        Note.new(Fraction(1, 8), Pitch(4, "A", SHARP)),
        Note.new(Fraction(1, 8), Pitch(4, "A")),
    ]
    assert list(
        Measure(notes, accidentals={Fraction(1, 4): {"A": FLAT}}).play(
            State(
                TimeSignature.new(4, 4),
                120,
                mezzo_forte,
                tailoff_factor=Fraction(0, 1),
            ),
        )
    ) == [
        Note.new(Fraction(1, 16), Pitch(4, "G", NATURAL), mezzo_forte),
        Note.new(Fraction(3, 16), Pitch(4, "A", NATURAL), mezzo_forte),
        Note.new(Fraction(1, 4), Pitch(4, "B", NATURAL), forte),
        Note.new(Fraction(1, 8), Pitch(4, "A", SHARP), mezzo_forte),
        Note.new(Fraction(1, 8), Pitch(4, "A", FLAT), mezzo_forte),
        Rest(Fraction(1, 4)),
    ]

    assert list(
        Measure(
            notes,
            time=TimeSignature.new(5, 4),
            dynamics={Fraction(1, 4): piano},
            keys={Fraction(1, 2): KEYS["C Major"]},
        ).play(
            State(
                TimeSignature.new(4, 4),
                120,
                mezzo_forte,
                KEYS["A♭ Major"],
                tailoff_factor=Fraction(0, 1),
            ),
        )
    ) == [
        Note.new(Fraction(1, 16), Pitch(4, "G", NATURAL), mezzo_forte),
        Note.new(Fraction(3, 16), Pitch(4, "A", FLAT), mezzo_forte),
        Note.new(Fraction(1, 4), Pitch(4, "B", FLAT), forte),
        Note.new(Fraction(1, 8), Pitch(4, "A", SHARP), piano),
        Note.new(Fraction(1, 8), Pitch(4, "A", NATURAL), piano),
        Rest(Fraction(1, 2)),
    ]

    # state changes
    state = State(
        TimeSignature.new(4, 4),
        120,
        mezzo_forte,
        KEYS["A♭ Major"],
        tailoff_factor=Fraction(0, 1),
    )
    iterator = Measure(
        notes,
        time=TimeSignature.new(3, 4),
        tempos={Fraction(1, 4): 240, Fraction(5, 8): 60},
        dynamics={Fraction(0, 4): forte, Fraction(1, 4): piano},
        keys={
            Fraction(1, 4): KEYS["C Major"],
            Fraction(1, 2): KEYS["C Minor"],
        },
    ).play(state)

    assert next(iterator).duration == Fraction(1, 16)
    assert state.time == TimeSignature.new(3, 4)
    assert state.tempo == 120
    assert state.dynamic == forte
    assert state.key == KEYS["A♭ Major"]

    assert next(iterator).duration == Fraction(3, 16)
    assert state.time == TimeSignature.new(3, 4)
    assert state.tempo == 120
    assert state.dynamic == forte
    assert state.key == KEYS["A♭ Major"]

    assert next(iterator).duration == Fraction(1, 4)
    assert state.time == TimeSignature.new(3, 4)
    assert state.tempo == 240
    assert state.dynamic == piano
    assert state.key == KEYS["C Major"]

    assert next(iterator).duration == Fraction(1, 8)
    assert state.time == TimeSignature.new(3, 4)
    assert state.tempo == 240
    assert state.dynamic == piano
    assert state.key == KEYS["C Minor"]

    assert next(iterator).duration == Fraction(1, 8)
    assert state.time == TimeSignature.new(3, 4)
    assert state.tempo == 60
    assert state.dynamic == piano
    assert state.key == KEYS["C Minor"]

    # illicit changes

    # time too short
    iterator = Measure(notes, time=TimeSignature.new(2, 4)).play(
        State(
            TimeSignature.new(4, 4),
            120,
            mezzo_forte,
            KEYS["A♭ Major"],
            tailoff_factor=Fraction(0, 1),
        )
    )
    next(iterator)
    next(iterator)
    next(iterator)
    with pytest.raises(ValueError):
        next(iterator)

    # before, mid-note, after-measure
    for skips, fraction in (
        (0, Fraction(-1, 2)),
        (2, Fraction(1, 8)),
        (5, Fraction(1, 1)),
    ):
        tempo_iterator = Measure(notes, tempos={fraction: 100}).play(
            State(
                TimeSignature.new(4, 4),
                120,
                mezzo_forte,
                KEYS["A♭ Major"],
                tailoff_factor=Fraction(0, 1),
            )
        )
        dynamic_iterator = Measure(notes, dynamics={fraction: piano}).play(
            State(
                TimeSignature.new(4, 4),
                120,
                mezzo_forte,
                KEYS["A♭ Major"],
                tailoff_factor=Fraction(0, 1),
            )
        )
        accidentals_iterator = Measure(notes, accidentals={fraction: {"C": FLAT}}).play(
            State(
                TimeSignature.new(4, 4),
                120,
                mezzo_forte,
                KEYS["A♭ Major"],
                tailoff_factor=Fraction(0, 1),
            )
        )
        key_iterator = Measure(notes, keys={fraction: KEYS["C Major"]}).play(
            State(
                TimeSignature.new(4, 4),
                120,
                mezzo_forte,
                KEYS["A♭ Major"],
                tailoff_factor=Fraction(0, 1),
            )
        )

        for _ in range(skips):
            next(tempo_iterator)
            next(dynamic_iterator)
            next(accidentals_iterator)
            next(key_iterator)

        with pytest.raises(ValueError):
            next(tempo_iterator)

        with pytest.raises(ValueError):
            next(dynamic_iterator)

        with pytest.raises(ValueError):
            next(accidentals_iterator)

        with pytest.raises(ValueError):
            next(key_iterator)

    # accent

    # easy mode
    assert list(
        Measure(
            [
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.ACCENT),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.MARCATO),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=None),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.STACCATO),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.STACCATISSIMO),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.TENUTO),
                Note.new(Fraction(2, 4), Pitch(4, "A"), accent=None),
            ]
        ).play(
            State(
                TimeSignature.new(9, 4),
                120,
                mezzo_forte,
                KEYS["A♭ Major"],
                tailoff_factor=Fraction(0, 1),
            )
        )
    ) == [
        Note.new(Fraction(1, 4), Pitch(4, "A", FLAT), mezzo_forte, Accent.ACCENT),
        Note.new(Fraction(1, 8), Pitch(4, "A", FLAT), mezzo_forte, Accent.ACCENT),
        Rest(Fraction(1, 8)),
        Note.new(Fraction(1, 4), Pitch(4, "A", FLAT), mezzo_forte, Accent.SLUR),
        Note.new(Fraction(1, 4), Pitch(4, "A", FLAT), mezzo_forte, None),
        Note.new(Fraction(1, 8), Pitch(4, "A", FLAT), mezzo_forte, None),
        Rest(Fraction(1, 8)),
        Note.new(Fraction(1, 16), Pitch(4, "A", FLAT), mezzo_forte, None),
        Rest(Fraction(3, 16)),
        Note.new(Fraction(1, 4), Pitch(4, "A", FLAT), mezzo_forte, None),
        Note.new(Fraction(1, 2), Pitch(4, "A", FLAT), mezzo_forte, None),
    ]

    # with tail-off
    assert list(
        Measure(
            [
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.ACCENT),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.MARCATO),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=None),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.STACCATO),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.STACCATISSIMO),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.TENUTO),
                Note.new(Fraction(1, 2), Pitch(4, "A"), accent=None),
            ]
        ).play(
            State(
                TimeSignature.new(9, 4),
                120,
                mezzo_forte,
                KEYS["A♭ Major"],
            )
        )
    ) == [
        Note.new(Fraction(3, 16), Pitch(4, "A", FLAT), mezzo_forte, Accent.ACCENT),
        Rest(Fraction(1, 16)),
        Note.new(Fraction(1, 8), Pitch(4, "A", FLAT), mezzo_forte, Accent.ACCENT),
        Rest(Fraction(1, 8)),
        Note.new(Fraction(1, 4), Pitch(4, "A", FLAT), mezzo_forte, Accent.SLUR),
        Note.new(Fraction(3, 16), Pitch(4, "A", FLAT), mezzo_forte, None),
        Rest(Fraction(1, 16)),
        Note.new(Fraction(1, 8), Pitch(4, "A", FLAT), mezzo_forte, None),
        Rest(Fraction(1, 8)),
        Note.new(Fraction(1, 16), Pitch(4, "A", FLAT), mezzo_forte, None),
        Rest(Fraction(3, 16)),
        Note.new(Fraction(1, 4), Pitch(4, "A", FLAT), mezzo_forte, None),
        Note.new(Fraction(7, 16), Pitch(4, "A", FLAT), mezzo_forte, None),
        Rest(Fraction(1, 16)),
    ]

    # illicit accents

    # should be safe unless preceded by a slur
    measure = Measure([Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.STACCATO)])
    assert list(
        measure.play(State(TimeSignature.new(1, 4), 120, mezzo_forte, KEYS["A♭ Major"]))
    ) == [
        Note.new(Fraction(1, 8), Pitch(4, "A", FLAT), mezzo_forte),
        Rest(Fraction(1, 8)),
    ]
    with pytest.raises(ValueError):
        list(
            measure.play(
                State(
                    TimeSignature.new(1, 4),
                    120,
                    mezzo_forte,
                    KEYS["A♭ Major"],
                    Accent.SLUR,
                ),
            )
        )

    assert list(
        Measure(
            [
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.ACCENT),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.ACCENT),
            ]
        ).play(State(TimeSignature.new(2, 4), 120, mezzo_forte, KEYS["A♭ Major"]))
    ) == [
        Note.new(Fraction(3, 16), Pitch(4, "A", FLAT), mezzo_forte, Accent.ACCENT),
        Rest(Fraction(1, 16)),
        Note.new(Fraction(3, 16), Pitch(4, "A", FLAT), mezzo_forte, Accent.ACCENT),
        Rest(Fraction(1, 16)),
    ]
    with pytest.raises(ValueError):
        list(
            Measure(
                [
                    Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                    Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.ACCENT),
                ]
            ).play(State(TimeSignature.new(2, 4), 120, mezzo_forte, KEYS["A♭ Major"]))
        )

    # many accents can't be long
    for accent in (
        Accent.ACCENT,
        Accent.MARCATO,
        Accent.STACCATO,
        Accent.STACCATISSIMO,
    ):
        list(
            Measure(
                [
                    Note.new(Fraction(1, 4), Pitch(4, "A"), accent=accent),
                    Note.new(Fraction(1, 4), Pitch(4, "A")),
                ]
            ).play(State(TimeSignature.new(2, 4), 120, mezzo_forte, KEYS["A♭ Major"]))
        )

        with pytest.raises(ValueError):
            list(
                Measure(
                    [
                        Note.new(Fraction(1, 2), Pitch(4, "A"), accent=accent),
                        Note.new(Fraction(1, 4), Pitch(4, "A")),
                    ]
                ).play(
                    State(TimeSignature.new(3, 4), 120, mezzo_forte, KEYS["A♭ Major"])
                )
            )


def test_part():
    from blooper.notes import Accent, Dynamic, Note, Rest, Tone
    from blooper.parts import COMMON_TIME, KEYS, WALTZ_TIME, Key, Measure, Part
    from blooper.pitch import FLAT, NATURAL, SHARP, Chord, Pitch

    piano = Dynamic.from_symbol("p")
    mezzo_forte = Dynamic.from_symbol("mf")
    forte = Dynamic.from_symbol("f")
    fortissimo = Dynamic.from_symbol("ff")

    assert Part([]).concurrence() == 0
    assert Part([Measure([])]).concurrence() == 0
    assert Part([Measure([Rest(Fraction(1, 4))])]).concurrence() == 0
    assert Part([Measure([Note.new(Fraction(1, 4), Pitch(4, "A"))])]).concurrence() == 1

    part = Part(
        [
            Measure(
                [
                    Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                    Note.new(Fraction(1, 8), Pitch(4, "A"), accent=Accent.SLUR),
                    Note.new(Fraction(1, 8), Pitch(4, "A"), accent=Accent.TENUTO),
                    Rest(Fraction(1, 4)),
                    Rest(Fraction(1, 4)),
                ],
                # tempo change twice in one held note
                tempos={Fraction(1, 4): 180, Fraction(3, 8): 240, Fraction(3, 4): 120},
                # change mid-held note should be ignored until new note
                dynamics={Fraction(1, 4): fortissimo},
                keys={Fraction(3, 4): Key.new("A", True, flats=["A"])},
            ),
            Measure(
                [
                    Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                    Note.new(
                        Fraction(1, 8), Pitch(4, "A", SHARP), accent=Accent.TENUTO
                    ),
                    Note.new(
                        Fraction(1, 8),
                        Pitch(4, "A", SHARP),
                        dynamic=piano,
                        accent=Accent.MARCATO,
                    ),
                    Note.new(Fraction(1, 4), Pitch(4, "B"), accent=Accent.ACCENT),
                    Note.new(
                        Fraction(1, 4), Pitch(4, "B", SHARP), accent=Accent.TENUTO
                    ),
                ],
                # tempo change on note change
                tempos={Fraction(0, 1): 60, Fraction(3, 8): 120},
                dynamics={Fraction(1, 4): mezzo_forte},
                keys={Fraction(1, 4): KEYS["C Major"]},
            ),
            Measure(
                [
                    Note.new(Fraction(1, 2), Pitch(3, "A"), accent=Accent.TENUTO),
                    Note.new(Fraction(1, 4), Pitch(3, "F", SHARP), accent=Accent.SLUR),
                ],
                time=WALTZ_TIME,
            ),
            Measure(
                [
                    Note.new(Fraction(1, 4), Pitch(3, "F", SHARP), accent=Accent.SLUR),
                    Note.new(
                        Fraction(1, 8), Pitch(3, "F", SHARP), accent=Accent.TENUTO
                    ),
                    Rest(Fraction(1, 2)),
                    Note.new(Fraction(1, 8), Pitch(3, "A"), accent=Accent.TENUTO),
                ],
                time=COMMON_TIME,
                keys={Fraction(0, 1): Key.new("A", True, flats=["A"])},
            ),
        ],
        dynamic=forte,
        key=KEYS["C Major"],
    )

    tones = list(part.tones(30_000))

    # sorry future me if you ever need to change this
    assert tones == [
        (0, 23_750, Tone(Pitch(4, "A", NATURAL), forte)),
        (46_250, 30_000, Tone(Pitch(4, "A", FLAT), fortissimo, Accent.SLUR)),
        (76_250, 15_000, Tone(Pitch(4, "A", SHARP), mezzo_forte)),
        (91_250, 3_750, Tone(Pitch(4, "A", SHARP), piano, Accent.ACCENT)),
        (98_750, 11_250, Tone(Pitch(4, "B", NATURAL), mezzo_forte, Accent.ACCENT)),
        (113_750, 15_000, Tone(Pitch(4, "B", SHARP), mezzo_forte)),
        (128_750, 30_000, Tone(Pitch(3, "A", NATURAL), mezzo_forte)),
        (158_750, 37_500, Tone(Pitch(3, "F", SHARP), mezzo_forte)),
        (226_250, 7_500, Tone(Pitch(3, "A", FLAT), mezzo_forte)),
    ]

    # really basic polyphonics test
    assert 4 == len(
        list(
            Part(
                [
                    [
                        # 1
                        Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                        # 2
                        Note.new(
                            Fraction(1, 8),
                            Chord(Pitch(4, "A"), Pitch(4, "B")),
                            accent=Accent.SLUR,
                        ),
                        Note.new(
                            Fraction(1, 8),
                            Chord(Pitch(4, "A"), Pitch(4, "B")),
                            accent=Accent.SLUR,
                        ),
                        Note.new(
                            Fraction(1, 8),
                            Chord(Pitch(4, "B"), Pitch(4, "A")),
                            accent=Accent.SLUR,
                        ),
                        # 3
                        Note.new(
                            Fraction(1, 8),
                            Chord(Pitch(4, "A"), Pitch(4, "B"), Pitch(4, "C")),
                            accent=Accent.SLUR,
                        ),
                        # 4
                        Note.new(Fraction(1, 4), Chord(Pitch(4, "A"), Pitch(4, "B"))),
                    ]
                ]
            ).tones(30_000)
        )
    )

    # slurs can't be followed by rests
    list(
        Part(
            [
                [
                    Note.new(Fraction(1, 4), Pitch(4, "A")),
                    Rest(Fraction(1, 4)),
                    Note.new(Fraction(1, 4), Pitch(4, "A")),
                ],
                [
                    Rest(Fraction(1, 4)),
                    Note.new(Fraction(1, 2), Pitch(4, "A")),
                ],
            ],
            time=WALTZ_TIME,
            dynamic=forte,
        ).tones(40_000)
    )

    # before rest within measure
    with pytest.raises(ValueError):
        list(
            Part(
                [
                    [
                        Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                        Rest(Fraction(1, 4)),
                        Note.new(Fraction(1, 4), Pitch(4, "A")),
                    ],
                    [
                        Rest(Fraction(1, 4)),
                        Note.new(Fraction(1, 2), Pitch(4, "A")),
                    ],
                ],
                time=WALTZ_TIME,
                tempo=120,
                dynamic=forte,
            ).tones(40_000)
        )

    # before rest between measures
    with pytest.raises(ValueError):
        list(
            Part(
                [
                    [
                        Note.new(Fraction(1, 4), Pitch(4, "A")),
                        Rest(Fraction(1, 4)),
                        Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                    ],
                    [
                        Rest(Fraction(1, 4)),
                        Note.new(Fraction(1, 2), Pitch(4, "A")),
                    ],
                ],
                time=WALTZ_TIME,
            ).tones(40_000)
        )

    # end of song
    with pytest.raises(ValueError):
        list(
            Part(
                [
                    [
                        Note.new(Fraction(1, 4), Pitch(4, "A")),
                        Rest(Fraction(1, 4)),
                        Note.new(Fraction(1, 4), Pitch(4, "A")),
                    ],
                    [
                        Rest(Fraction(1, 4)),
                        Note.new(Fraction(1, 2), Pitch(4, "A"), accent=Accent.SLUR),
                    ],
                ],
                time=WALTZ_TIME,
            ).tones(40_000)
        )
