from fractions import Fraction
from pathlib import Path

from blooper import (
    DOUBLE_FLAT,
    FLAT,
    SHARP,
    Accent,
    Measure,
    Mixer,
    Note,
    Part,
    Pitch,
    Rest,
    Synthesizer,
    Tempo,
    TimeSignature,
    record,
)

instrument = Synthesizer("triangle")


piano_melody_right = Part(
    [
        [
            Note(Fraction(1, 4), Pitch(5, "C")),
            # Blooper doesn't support grace notes
            Note(Fraction(1, 64), Pitch(5, "C")),
            Note(Fraction(3, 64), Pitch(4, "B")),
            Note(Fraction(1, 16), Pitch(4, "G")),
            Note(Fraction(1, 16), Pitch(4, "D")),
            Note(Fraction(1, 16), Pitch(4, "B")),
            # Admitedly, triplets look weird expessed this way
            Note(Fraction(1, 12), Pitch(4, "A")),
            Note(Fraction(1, 12), Pitch(5, "C")),
            Note(Fraction(1, 12), Pitch(4, "B")),
            Note(Fraction(1, 12), Pitch(4, "G")),
            Note(Fraction(1, 12), Pitch(4, "E")),
            Note(Fraction(1, 12), Pitch(4, "B")),
        ],
        Measure(
            [
                Note(Fraction(1, 8), Pitch(4, "A")),
                Note(Fraction(1, 8), Pitch(5, "C")),
                # Grace
                Note(Fraction(1, 32), Pitch(5, "C")),
                Note(Fraction(3, 32), Pitch(4, "B")),
                Note(Fraction(1, 8), Pitch(4, "A")),
                Note(Fraction(1, 8), Pitch(5, "D")),
                # Grace
                Note(Fraction(1, 32), Pitch(4, "G")),
                Note(Fraction(3, 32), Pitch(4, "A")),
            ],
            time=TimeSignature.new(3, 4),
        ),
        Measure(
            [
                # pentuplet
                Note(Fraction(1, 20), Pitch(5, "C")),
                # grace pentuplet
                Note(Fraction(1, 80), Pitch(5, "C")),
                Note(Fraction(3, 80), Pitch(4, "B")),
                Note(Fraction(1, 20), Pitch(4, "G")),
                Note(Fraction(1, 20), Pitch(4, "E")),
                Note(Fraction(1, 20), Pitch(4, "B")),
                # slur onto the same note is a tie
                Note(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                Note(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                Note(Fraction(1, 8), Pitch(4, "A")),
                Note(Fraction(1, 8), Pitch(5, "C"), accent=Accent.SLUR),
            ],
            time=TimeSignature.new(4, 4),
        ),
        Measure(
            [
                Note(Fraction(1, 4), Pitch(5, "C"), accent=Accent.SLUR),
                # Ok so, the score I'm working off appears to be
                # mislabelled but to the best of my knowledge, the
                # second beat is:
                # a triplet
                # 3 pentuplets (with a grace note on the first)
                # a triplet (with a grace note)
                # But those 3 pentuplets must actually be 1/3 of a triplet?
                Note(Fraction(1, 12), Pitch(5, "C")),
                # gracenote on a note that's 1/3 of a triplet
                Note(Fraction(1, 144), Pitch(5, "C")),
                Note(Fraction(3, 144), Pitch(4, "B")),
                Note(Fraction(1, 36), Pitch(4, "G")),
                Note(Fraction(1, 36), Pitch(4, "B")),
                Note(Fraction(1, 48), Pitch(5, "C")),
                Note(Fraction(3, 48), Pitch(4, "B", FLAT)),
            ],
            time=TimeSignature.new(2, 4),
        ),
        Measure(
            [
                Note(Fraction(1, 12), Pitch(4, "A")),
                Note(Fraction(1, 48), Pitch(5, "C")),  # grace
                Note(Fraction(3, 48), Pitch(4, "B", FLAT)),
                Note(Fraction(1, 12), Pitch(4, "A")),
                Rest(Fraction(1, 8)),
                Note(Fraction(1, 16), Pitch(5, "C")),
                Rest(Fraction(1, 16)),
                Rest(Fraction(1, 4)),
            ],
            time=TimeSignature.new(3, 4),
        ),
        [
            Rest(Fraction(1, 4)),
            Rest(Fraction(1, 4)),
            Rest(Fraction(1, 8)),
            Note(Fraction(1, 8), Pitch(4, "C"), accent=Accent.SLUR),
        ],
        Measure(
            [
                Note(Fraction(1, 4), Pitch(5, "C")),
                Note(Fraction(1, 64), Pitch(5, "C")),  # grace
                Note(Fraction(3, 64), Pitch(4, "B")),
                Note(Fraction(1, 16), Pitch(4, "G")),
                Note(Fraction(1, 16), Pitch(4, "E")),
                Note(Fraction(1, 16), Pitch(4, "B")),
            ],
            time=TimeSignature.new(2, 4),
        ),
        Measure(
            [
                Note(Fraction(1, 8), Pitch(4, "A")),
                Note(Fraction(1, 8), Pitch(5, "C")),
                Note(Fraction(1, 32), Pitch(5, "C")),
                Note(Fraction(3, 32), Pitch(4, "B")),
                Note(Fraction(1, 8), Pitch(4, "A")),
                Note(Fraction(1, 8), Pitch(5, "D")),
                Note(Fraction(1, 32), Pitch(4, "G")),
                Note(Fraction(3, 32), Pitch(4, "A")),
            ],
            time=TimeSignature.new(3, 4),
        ),
        Measure(
            [
                Note(Fraction(1, 20), Pitch(5, "C")),
                Note(Fraction(1, 80), Pitch(5, "C")),  # grace
                Note(Fraction(3, 80), Pitch(4, "B")),
                Note(Fraction(1, 20), Pitch(4, "G")),
                Note(Fraction(1, 20), Pitch(4, "E")),
                Note(Fraction(1, 20), Pitch(4, "B")),
                Note(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
            ],
            time=TimeSignature.new(2, 4),
        ),
        [Note(Fraction(1, 2), Pitch(4, "A"), accent=Accent.SLUR)],
        [Note(Fraction(1, 2), Pitch(4, "A"), accent=Accent.SLUR)],
        [Note(Fraction(1, 2), Pitch(4, "A"))],
    ],
    tempo=Tempo.LENTO,
)

piano_melody_left = Part(
    [
        # measure will be filled with rests as necessary, so you can pass
        # an empty array for whole rests
        [],
        Measure([], time=TimeSignature.new(3, 4)),
        Measure([], time=TimeSignature.new(4, 4)),
        Measure([], time=TimeSignature.new(2, 4)),
        Measure(
            [
                Rest(Fraction(1, 4)),
                Note(Fraction(1, 2), Pitch(4, "G", FLAT)),
            ],
            time=TimeSignature.new(3, 4),
        ),
        Measure(
            [
                Note(Fraction(1, 24), Pitch(4, "F")),
                Note(Fraction(1, 24), Pitch(4, "D", SHARP)),
                Note(Fraction(1, 96), Pitch(4, "F")),  # grace
                Note(Fraction(3, 96), Pitch(4, "E")),
                Note(Fraction(1, 24), Pitch(4, "C")),
                Note(Fraction(1, 96), Pitch(4, "E")),  # grace
                Note(Fraction(3, 96), Pitch(4, "D")),
                Note(Fraction(1, 24), Pitch(3, "B"), accent=Accent.SLUR),
                Note(Fraction(1, 8), Pitch(3, "B")),
                Rest(Fraction(1, 8)),
            ],
            accidentals={Fraction(0, 1): {"C": SHARP, "F": SHARP}},
        ),
        Measure([], time=TimeSignature.new(2, 4)),
        Measure([], time=TimeSignature.new(3, 4)),
        Measure([], time=TimeSignature.new(2, 4)),
        [],
        [],
        [],
    ],
    tempo=Tempo.LENTO,
)

piano_harmony_right = Part(
    [
        [],
        Measure(
            [
                Note(Fraction(1, 4), Pitch(4, "C"), accent=Accent.SLUR),
                Note(Fraction(1, 12), Pitch(4, "C")),
                Note(Fraction(1, 6), Pitch(4, "D"), accent=Accent.SLUR),
                Note(Fraction(1, 4), Pitch(4, "D"), accent=Accent.SLUR),
            ],
            time=TimeSignature.new(3, 4),
            accidentals={Fraction(0, 1): {"C": SHARP}},
        ),
        Measure(
            [
                Note(Fraction(1, 4), Pitch(4, "D")),
                Note(Fraction(1, 4), Pitch(4, "C"), accent=Accent.SLUR),
                Note(Fraction(1, 4), Pitch(4, "C"), accent=Accent.SLUR),
                Note(Fraction(1, 8), Pitch(4, "C")),
                Rest(Fraction(1, 8)),
            ],
            time=TimeSignature.new(4, 4),
            accidentals={Fraction(1, 4): {"C": SHARP}},
        ),
        Measure(
            [
                Note(Fraction(3, 8), (Pitch(3, "A", FLAT), Pitch(4, "D", FLAT))),
                Note(
                    Fraction(1, 8), (Pitch(3, "G"), Pitch(4, "C")), accent=Accent.SLUR
                ),
            ],
            time=TimeSignature.new(2, 4),
        ),
        Measure(
            [
                Note(Fraction(1, 12), (Pitch(3, "G"), Pitch(4, "C"))),
                Note(Fraction(1, 6), (Pitch(3, "G", FLAT), Pitch(3, "B"))),
                Note(
                    Fraction(1, 4),
                    (Pitch(3, "F"), Pitch(3, "B", FLAT)),
                    accent=Accent.SLUR,
                ),
                Note(Fraction(1, 12), (Pitch(3, "F"), Pitch(3, "B", FLAT))),
                Note(
                    Fraction(1, 12), (Pitch(3, "F", FLAT), Pitch(3, "B", DOUBLE_FLAT))
                ),
                Note(Fraction(1, 12), (Pitch(3, "E", FLAT), Pitch(3, "A", FLAT))),
            ],
            time=TimeSignature.new(3, 4),
        ),
        [
            Note(Fraction(1, 12), (Pitch(3, "D"), Pitch(3, "G"))),
            Note(Fraction(1, 12), (Pitch(3, "C", SHARP), Pitch(3, "F", SHARP))),
            Note(Fraction(1, 12), (Pitch(3, "C"), Pitch(3, "F"))),
            Note(Fraction(1, 12), (Pitch(2, "B"), Pitch(3, "E"))),
            Note(Fraction(1, 12), (Pitch(2, "B", FLAT), Pitch(3, "E", FLAT))),
            Note(Fraction(1, 12), (Pitch(2, "A"), Pitch(3, "D"))),
            Note(
                Fraction(1, 4),
                (Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                accent=Accent.SLUR,
            ),
        ],
        Measure(
            [
                Note(
                    Fraction(1, 2),
                    (Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                    accent=Accent.SLUR,
                )
            ],
            time=TimeSignature.new(2, 4),
        ),
        Measure(
            [
                Note(
                    Fraction(1, 4),
                    (Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                    accent=Accent.SLUR,
                ),
                Note(Fraction(1, 12), (Pitch(2, "G", SHARP), Pitch(3, "C", SHARP))),
                Note(Fraction(1, 12), (Pitch(2, "A"), Pitch(3, "D"))),
                Note(
                    Fraction(1, 12),
                    (Pitch(2, "A", SHARP), Pitch(3, "D", SHARP)),
                    accent=Accent.SLUR,
                ),
                Note(Fraction(1, 8), (Pitch(2, "A", SHARP), Pitch(3, "D", SHARP))),
                Note(Fraction(1, 8), (Pitch(2, "A"), Pitch(3, "D"))),
            ],
            time=TimeSignature.new(3, 4),
        ),
        Measure([], time=TimeSignature.new(2, 4)),
        Measure(
            [
                Note(Fraction(1, 8), Pitch(4, "C")),
                Note(Fraction(1, 8), Pitch(4, "F")),
                Note(Fraction(1, 48), Pitch(4, "F")),  # grace
                Note(Fraction(3, 48), Pitch(4, "D")),
                Note(Fraction(1, 12), Pitch(4, "C")),
                Note(Fraction(1, 12), Pitch(4, "F")),
            ],
            accidentals={Fraction(0, 1): {"C": SHARP, "D": SHARP, "F": SHARP}},
        ),
        Measure(
            [
                Note(Fraction(1, 48), Pitch(4, "F")),  # grace
                Note(Fraction(3, 48), Pitch(4, "D")),
                Note(Fraction(1, 12), Pitch(4, "C")),
                Note(Fraction(1, 24), Pitch(4, "F")),
                Rest(Fraction(1, 24)),
                Rest(Fraction(1, 12)),
                Note(Fraction(1, 24), Pitch(4, "G")),
                Note(Fraction(1, 24), Pitch(4, "D")),
                Note(Fraction(1, 24), Pitch(4, "F")),
                Note(Fraction(1, 24), Pitch(4, "C")),
            ],
            accidentals={
                Fraction(0, 1): {"C": SHARP, "D": SHARP, "F": SHARP, "G": SHARP}
            },
        ),
        [Note(Fraction(1, 2), Pitch(4, "D", SHARP))],
    ],
    tempo=Tempo.LENTO,
)

piano_harmony_left = Part(
    [
        [],
        Measure([], time=TimeSignature.new(3, 4)),
        Measure([], time=TimeSignature.new(4, 4)),
        Measure([], time=TimeSignature.new(2, 4)),
        Measure([], time=TimeSignature.new(3, 4)),
        [],
        Measure([], time=TimeSignature.new(2, 4)),
        Measure([], time=TimeSignature.new(3, 4)),
        Measure(
            [
                Note(
                    Fraction(1, 2),
                    (Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                    accent=Accent.SLUR,
                )
            ],
            time=TimeSignature.new(2, 4),
        ),
        [
            Note(
                Fraction(1, 2),
                (Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                accent=Accent.SLUR,
            )
        ],
        [
            Note(
                Fraction(1, 2),
                (Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                accent=Accent.SLUR,
            )
        ],
        [Note(Fraction(1, 2), (Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)))],
    ],
    tempo=Tempo.LENTO,
)


record(
    Path("rite.wav"),
    Mixer.even(
        (instrument, piano_melody_right),
        (instrument, piano_melody_left),
        (instrument, piano_harmony_right),
        (instrument, piano_harmony_left),
    ),
)
