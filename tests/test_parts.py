from fractions import Fraction

import pytest


def test_key():
    from blooper.parts import Key

    flat = Fraction(-1, 2)
    natural = Fraction(0, 1)
    sharp = Fraction(1, 2)

    key = Key("C", True, {})

    assert key.accidental("C") == natural
    assert key.accidental("D") == natural
    assert key.accidental("E") == natural
    assert key.accidental("F") == natural
    assert key.accidental("G") == natural
    assert key.accidental("A") == natural
    assert key.accidental("B") == natural

    key = Key("C", True, {"G": Fraction(1, 1), "A": flat})

    assert key.accidental("C") == natural
    assert key.accidental("D") == natural
    assert key.accidental("E") == natural
    assert key.accidental("F") == natural
    assert key.accidental("G") == Fraction(1, 1)
    assert key.accidental("A") == flat
    assert key.accidental("B") == natural

    key = Key.new("C", True)

    assert key.name == "C Major"
    assert key.accidental("C") == natural
    assert key.accidental("D") == natural
    assert key.accidental("E") == natural
    assert key.accidental("F") == natural
    assert key.accidental("G") == natural
    assert key.accidental("A") == natural
    assert key.accidental("B") == natural

    key = Key.new("G", True, sharps=("F",))

    assert key.name == "G Major"
    assert key.accidental("C") == natural
    assert key.accidental("D") == natural
    assert key.accidental("E") == natural
    assert key.accidental("F") == sharp
    assert key.accidental("G") == natural
    assert key.accidental("A") == natural
    assert key.accidental("B") == natural

    key = Key.new("A", True, sharps=("C", "F", "G"))

    assert key.name == "A Major"
    assert key.accidental("C") == sharp
    assert key.accidental("D") == natural
    assert key.accidental("E") == natural
    assert key.accidental("F") == sharp
    assert key.accidental("G") == sharp
    assert key.accidental("A") == natural
    assert key.accidental("B") == natural

    key = Key.new("F", True, sharps=("F", "G", "A", "C", "D", "E"))

    assert key.name == "F♯ Major"
    assert key.accidental("C") == sharp
    assert key.accidental("D") == sharp
    assert key.accidental("E") == sharp
    assert key.accidental("F") == sharp
    assert key.accidental("G") == sharp
    assert key.accidental("A") == sharp
    assert key.accidental("B") == natural

    key = Key.new("B", False, flats=("B", "D", "E", "G", "A"))

    assert key.name == "B♭ Minor"
    assert key.accidental("C") == natural
    assert key.accidental("D") == flat
    assert key.accidental("E") == flat
    assert key.accidental("F") == natural
    assert key.accidental("G") == flat
    assert key.accidental("A") == flat
    assert key.accidental("B") == flat

    with pytest.raises(ValueError):
        Key.new("B", False, flats=("B", "D", "E", "G", "A", "A"))


def test_time_signature():
    from blooper.parts import TimeSignature

    assert TimeSignature(4, 4) != TimeSignature(1, 1)
    assert str(TimeSignature(4, 4)) == "4/4"
    assert str(TimeSignature(3, 4)) == "3/4"
    assert str(TimeSignature(7, 8)) == "7/8"


def test_part_validate_accent():
    from blooper.notes import Accent, Note
    from blooper.parts import Part
    from blooper.pitch import Pitch

    duration = Fraction(1, 4)
    long_duration = Fraction(1, 2)
    pitch = Pitch(4, "A")
    beat_size = Fraction(1, 4)
    long_beat_size = Fraction(1, 2)

    minimal = {None, Accent.TENUTO, Accent.SLUR}
    for accent in (None, *iter(Accent)):
        for previous in (None, *iter(Accent)):
            if previous == Accent.SLUR:
                if accent in minimal:
                    Part.validate_accent(
                        Note(duration, pitch, accent=accent), beat_size, previous
                    )
                else:
                    with pytest.raises(ValueError):
                        Part.validate_accent(
                            Note(duration, pitch, accent=accent), beat_size, previous
                        )
            else:
                Part.validate_accent(
                    Note(duration, pitch, accent=accent), beat_size, previous
                )
                Part.validate_accent(
                    Note(duration, pitch, accent=accent), long_beat_size, previous
                )
                Part.validate_accent(
                    Note(long_duration, pitch, accent=accent), long_beat_size, previous
                )

            if accent in minimal:
                Part.validate_accent(
                    Note(long_duration, pitch, accent=accent), beat_size, previous
                )
            else:
                with pytest.raises(ValueError):
                    Part.validate_accent(
                        Note(long_duration, pitch, accent=accent), beat_size, previous
                    )


def test_part_adjust_duration():
    from blooper.notes import Accent, Dynamic, Note
    from blooper.parts import Key, Part, TimeSignature
    from blooper.pitch import Pitch

    pitch = Pitch(4, "A")

    # this would be a classmethod but we want to make it easy to change
    # tailoff factor. As such, we can just pass garbage for all this.
    # Maybe there's some bigger lesson about this class. hmm.
    part = Part(TimeSignature(4, 4), 120, Dynamic.from_symbol("mf"), [])

    half_note = Fraction(1, 2)
    quarter_note = Fraction(1, 4)
    eighth_note = Fraction(1, 8)

    forte = Dynamic.from_symbol("f")

    # no accent and Accent.Accent means 3/4 length (kind of)
    for accent in (None, Accent.ACCENT):
        assert part.adjust_duration(
            Note(half_note, pitch, accent=accent), quarter_note
        ) == Note(Fraction(7, 16), pitch, accent=accent)
        assert part.adjust_duration(
            Note(quarter_note, pitch, accent=accent), quarter_note
        ) == Note(Fraction(3, 16), pitch, accent=accent)
        assert part.adjust_duration(
            Note(eighth_note, pitch, accent=accent, dynamic=forte), quarter_note
        ) == Note(Fraction(3, 32), pitch, accent=accent, dynamic=forte)

    # MARCATO is STACCATO + ACCENT
    assert part.adjust_duration(
        Note(half_note, pitch, accent=Accent.MARCATO), quarter_note
    ) == Note(Fraction(1, 4), pitch, accent=Accent.ACCENT)
    assert part.adjust_duration(
        Note(quarter_note, pitch, accent=Accent.MARCATO), quarter_note
    ) == Note(Fraction(1, 8), pitch, accent=Accent.ACCENT)
    assert part.adjust_duration(
        Note(eighth_note, pitch, accent=Accent.MARCATO), quarter_note
    ) == Note(Fraction(1, 16), pitch, accent=Accent.ACCENT)

    assert part.adjust_duration(
        Note(half_note, pitch, accent=Accent.STACCATO), quarter_note
    ) == Note(Fraction(1, 4), pitch)
    assert part.adjust_duration(
        Note(quarter_note, pitch, accent=Accent.STACCATO), quarter_note
    ) == Note(Fraction(1, 8), pitch)
    assert part.adjust_duration(
        Note(eighth_note, pitch, accent=Accent.STACCATO), quarter_note
    ) == Note(Fraction(1, 16), pitch)

    assert part.adjust_duration(
        Note(half_note, pitch, accent=Accent.STACCATISSIMO), quarter_note
    ) == Note(Fraction(1, 8), pitch)
    assert part.adjust_duration(
        Note(quarter_note, pitch, accent=Accent.STACCATISSIMO), quarter_note
    ) == Note(Fraction(1, 16), pitch)
    assert part.adjust_duration(
        Note(eighth_note, pitch, accent=Accent.STACCATISSIMO), quarter_note
    ) == Note(Fraction(1, 32), pitch)

    assert part.adjust_duration(
        Note(half_note, pitch, accent=Accent.TENUTO), quarter_note
    ) == Note(half_note, pitch)
    assert part.adjust_duration(
        Note(quarter_note, pitch, accent=Accent.TENUTO), quarter_note
    ) == Note(quarter_note, pitch)
    assert part.adjust_duration(
        Note(eighth_note, pitch, accent=Accent.TENUTO), quarter_note
    ) == Note(eighth_note, pitch)

    assert part.adjust_duration(
        Note(half_note, pitch, accent=Accent.SLUR), quarter_note
    ) == Note(half_note, pitch, accent=Accent.SLUR)
    assert part.adjust_duration(
        Note(quarter_note, pitch, accent=Accent.SLUR), quarter_note
    ) == Note(quarter_note, pitch, accent=Accent.SLUR)
    assert part.adjust_duration(
        Note(eighth_note, pitch, accent=Accent.SLUR), quarter_note
    ) == Note(eighth_note, pitch, accent=Accent.SLUR)

    # different beat size
    assert part.adjust_duration(Note(half_note, pitch), eighth_note) == Note(
        Fraction(15, 32), pitch
    )
    assert part.adjust_duration(Note(quarter_note, pitch), eighth_note) == Note(
        Fraction(7, 32), pitch
    )
    assert part.adjust_duration(Note(eighth_note, pitch), eighth_note) == Note(
        Fraction(3, 32), pitch
    )

    assert part.adjust_duration(
        Note(half_note, pitch, accent=Accent.MARCATO), eighth_note
    ) == Note(Fraction(1, 4), pitch, accent=Accent.ACCENT)
    assert part.adjust_duration(
        Note(quarter_note, pitch, accent=Accent.MARCATO), eighth_note
    ) == Note(Fraction(1, 8), pitch, accent=Accent.ACCENT)
    assert part.adjust_duration(
        Note(eighth_note, pitch, accent=Accent.MARCATO), eighth_note
    ) == Note(Fraction(1, 16), pitch, accent=Accent.ACCENT)

    # different drop-off
    part = Part(
        TimeSignature(4, 4),
        120,
        Dynamic.from_symbol("mf"),
        [],
        Key.new("A", True),
        _tailoff_factor=Fraction(3, 16),
    )
    assert part.adjust_duration(Note(half_note, pitch), quarter_note) == Note(
        Fraction(29, 64), pitch
    )
    assert part.adjust_duration(Note(quarter_note, pitch), quarter_note) == Note(
        Fraction(13, 64), pitch
    )
    assert part.adjust_duration(Note(eighth_note, pitch), quarter_note) == Note(
        Fraction(13, 128), pitch
    )

    # 0 drop off
    part = Part(
        TimeSignature(4, 4),
        120,
        Dynamic.from_symbol("mf"),
        [],
        _tailoff_factor=Fraction(0, 1),
    )
    assert part.adjust_duration(Note(half_note, pitch), quarter_note) == Note(
        half_note, pitch
    )
    assert part.adjust_duration(Note(quarter_note, pitch), quarter_note) == Note(
        quarter_note, pitch
    )
    assert part.adjust_duration(Note(eighth_note, pitch), quarter_note) == Note(
        eighth_note, pitch
    )


def test_part():
    from blooper.notes import Accent, Dynamic, Note, Rest, Tone
    from blooper.parts import KEYS, Part, TimeSignature
    from blooper.pitch import Pitch

    common_time = TimeSignature(4, 4)
    waltz_time = TimeSignature(3, 4)

    piano = Dynamic.from_symbol("p")
    mezzo_forte = Dynamic.from_symbol("mf")
    forte = Dynamic.from_symbol("f")
    fortissimo = Dynamic.from_symbol("ff")

    # why no non-accented notes? this was written before no accent and
    # Accent.ACCENT became not full-length. We do have one Accent.ACCENT
    part = Part(
        common_time,
        120,
        forte,
        [
            [
                Note(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                Note(Fraction(1, 8), Pitch(4, "A"), accent=Accent.SLUR),
                Note(Fraction(1, 8), Pitch(4, "A"), accent=Accent.TENUTO),
                Rest(Fraction(1, 4)),
                Rest(Fraction(1, 4)),
            ],
            [
                Note(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                Note(
                    Fraction(1, 8),
                    Pitch(4, "A", Fraction(1, 2)),
                    accent=Accent.TENUTO,
                ),
                Note(
                    Fraction(1, 8),
                    Pitch(4, "A", Fraction(1, 2)),
                    dynamic=piano,
                    accent=Accent.MARCATO,
                ),
                Note(Fraction(1, 4), Pitch(4, "B"), accent=Accent.ACCENT),
                Note(
                    Fraction(1, 4), Pitch(4, "B", Fraction(1, 2)), accent=Accent.TENUTO
                ),
            ],
            [
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.TENUTO),
                Note(Fraction(1, 4), Pitch(3, "F", Fraction(1, 2)), accent=Accent.SLUR),
            ],
            [
                Note(Fraction(1, 4), Pitch(3, "F", Fraction(1, 2)), accent=Accent.SLUR),
                Note(
                    Fraction(1, 8), Pitch(3, "F", Fraction(1, 2)), accent=Accent.TENUTO
                ),
                Rest(Fraction(1, 2)),
                Note(Fraction(1, 8), Pitch(3, "A"), accent=Accent.TENUTO),
            ],
        ],
        KEYS["C Major"],
        time_changes={2: waltz_time, 3: common_time},
        tempo_changes={
            # tempo change twice in one held note
            0: {Fraction(1, 4): 180, Fraction(3, 8): 240, Fraction(3, 4): 120},
            # tempo change on note change
            1: {Fraction(0, 1): 60, Fraction(3, 8): 120},
        },
        dynamic_changes={
            # change mid-held note should be ignored until new note
            0: {Fraction(1, 4): fortissimo},
            1: {Fraction(1, 4): mezzo_forte},
        },
    )

    tones = list(part.tones(30_000))

    # sorry future me if you ever need to change this
    assert tones == [
        (0, Tone(23_750, Pitch(4, "A"), forte)),
        (46_250, Tone(30_000, Pitch(4, "A"), fortissimo, Accent.SLUR)),
        (76_250, Tone(15_000, Pitch(4, "A", Fraction(1, 2)), mezzo_forte)),
        (91_250, Tone(3_750, Pitch(4, "A", Fraction(1, 2)), piano, Accent.ACCENT)),
        (98_750, Tone(11_250, Pitch(4, "B"), mezzo_forte, Accent.ACCENT)),
        (113_750, Tone(15_000, Pitch(4, "B", Fraction(1, 2)), mezzo_forte)),
        (128_750, Tone(30_000, Pitch(3, "A"), mezzo_forte)),
        (158_750, Tone(37_500, Pitch(3, "F", Fraction(1, 2)), mezzo_forte)),
        (226_250, Tone(7_500, Pitch(3, "A"), mezzo_forte)),
    ]

    # illegal music

    # tempo/dynamic changes in notes
    # make sure it works right first
    part = Part(
        common_time,
        120,
        forte,
        [
            [
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.TENUTO),
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.TENUTO),
            ]
        ],
        tempo_changes={0: {Fraction(1, 2): 240}},
        dynamic_changes={0: {Fraction(1, 2): fortissimo}},
    )

    # You may be thinking: hey, this is a weird way to write this. It is.
    # Catching a tempo/dynamic change that happens in a note happens
    # after we've already yeilded the tone in question. We would need to
    # either duplicate this check (because yielding a note only happens
    # in one of 3 cases [no yield on rests/ties]) and/or we'd miss it
    # happening in the very last note of a part. If we ever need to
    # guarantee all supplied tones prior to a crash are correct we will
    # need to duplicate but not yet.
    generator = part.tones(30_000)
    assert next(generator) == (0, Tone(30_000, Pitch(3, "A"), forte))
    assert next(generator) == (30_000, Tone(15_000, Pitch(3, "A"), fortissimo))
    with pytest.raises(StopIteration):
        next(generator)

    # don't change tempo within a note
    part = Part(
        common_time,
        120,
        forte,
        [
            [
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.TENUTO),
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.TENUTO),
            ]
        ],
        tempo_changes={0: {Fraction(3, 4): 240}},
        dynamic_changes={0: {Fraction(1, 2): fortissimo}},
    )
    generator = part.tones(30_000)
    assert next(generator) == (0, Tone(30_000, Pitch(3, "A"), forte))
    next(generator)  # will be wrong. we don't care, it will crash next iteration
    with pytest.raises(ValueError):
        next(generator)

    # don't change dynamic within a note
    part = Part(
        common_time,
        120,
        forte,
        [
            [
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.TENUTO),
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.TENUTO),
            ]
        ],
        tempo_changes={0: {Fraction(1, 2): 240}},
        dynamic_changes={0: {Fraction(3, 4): fortissimo}},
    )
    generator = part.tones(30_000)
    assert next(generator) == (0, Tone(30_000, Pitch(3, "A"), forte))
    next(generator)  # will be wrong. we don't care, it will crash next iteration
    with pytest.raises(ValueError):
        next(generator)

    # misplaced accents
    # make sure it works
    part = Part(
        common_time,
        120,
        forte,
        [
            [
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.TENUTO),
                Rest(Fraction(1, 4)),
                Note(Fraction(1, 8), Pitch(3, "A"), accent=Accent.SLUR),
                Note(Fraction(1, 8), Pitch(3, "A"), accent=Accent.TENUTO),
            ],
            [Note(Fraction(1, 1), Pitch(3, "A"), accent=Accent.TENUTO)],
        ],
        dynamic_changes={1: {Fraction(0, 1): piano}},
    )

    generator = part.tones(30_000)
    assert next(generator) == (0, Tone(30_000, Pitch(3, "A"), forte))
    assert next(generator) == (45_000, Tone(15_000, Pitch(3, "A"), forte))
    assert next(generator) == (60_000, Tone(60_000, Pitch(3, "A"), piano))
    with pytest.raises(StopIteration):
        next(generator)

    # can't staccato a long note
    part = Part(
        common_time,
        120,
        forte,
        [
            [
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.STACCATO),
                Rest(Fraction(1, 4)),
                Note(Fraction(1, 8), Pitch(3, "A"), accent=Accent.SLUR),
                Note(Fraction(1, 8), Pitch(3, "A"), accent=Accent.TENUTO),
            ],
            [Note(Fraction(1, 1), Pitch(3, "A"), accent=Accent.TENUTO)],
        ],
        dynamic_changes={1: {Fraction(0, 1): piano}},
    )

    generator = part.tones(30_000)
    with pytest.raises(ValueError):
        next(generator)

    # can't slur into a rest
    part = Part(
        common_time,
        120,
        forte,
        [
            [
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.SLUR),
                Rest(Fraction(1, 4)),
                Note(Fraction(1, 8), Pitch(3, "A"), accent=Accent.SLUR),
                Note(Fraction(1, 8), Pitch(3, "A"), accent=Accent.TENUTO),
            ],
            [Note(Fraction(1, 1), Pitch(3, "A"), accent=Accent.TENUTO)],
        ],
        dynamic_changes={1: {Fraction(0, 1): piano}},
    )

    generator = part.tones(30_000)
    with pytest.raises(ValueError):
        next(generator)

    # can't staccato after a slur
    part = Part(
        common_time,
        120,
        forte,
        [
            [
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.TENUTO),
                Rest(Fraction(1, 4)),
                Note(Fraction(1, 8), Pitch(3, "A"), accent=Accent.SLUR),
                Note(Fraction(1, 8), Pitch(3, "A"), accent=Accent.STACCATO),
            ],
            [Note(Fraction(1, 1), Pitch(3, "A"), accent=Accent.TENUTO)],
        ],
        dynamic_changes={1: {Fraction(0, 1): piano}},
    )

    generator = part.tones(30_000)
    assert next(generator) == (0, Tone(30_000, Pitch(3, "A"), forte))
    with pytest.raises(ValueError):
        next(generator)

    # can't slur off the end of the piece
    part = Part(
        common_time,
        120,
        forte,
        [
            [
                Note(Fraction(1, 2), Pitch(3, "A"), accent=Accent.TENUTO),
                Rest(Fraction(1, 4)),
                Note(Fraction(1, 8), Pitch(3, "A"), accent=Accent.SLUR),
                Note(Fraction(1, 8), Pitch(3, "A"), accent=Accent.TENUTO),
            ],
            [Note(Fraction(1, 1), Pitch(3, "A"), accent=Accent.SLUR)],
        ],
        dynamic_changes={1: {Fraction(0, 1): piano}},
    )

    generator = part.tones(30_000)
    assert next(generator) == (0, Tone(30_000, Pitch(3, "A"), forte))
    assert next(generator) == (45_000, Tone(15_000, Pitch(3, "A"), forte))
    with pytest.raises(ValueError):
        next(generator)
