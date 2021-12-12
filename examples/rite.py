from fractions import Fraction
from pathlib import Path

from blooper import (
    DOUBLE_FLAT,
    FLAT,
    SHARP,
    Accent,
    Chord,
    Grace,
    Measure,
    Mixer,
    Note,
    Part,
    Pitch,
    Rest,
    Synthesizer,
    Tempo,
    TimeSignature,
    Tone,
    Triplet,
    Tuplet,
    record,
)

instrument = Synthesizer("triangle")


piano_melody_right = Part(
    [
        [
            Note.new(Fraction(1, 4), Pitch(5, "C")),
            Grace(Pitch(5, "C"), Note.new(Fraction(1, 16), Pitch(4, "B"))),
            Note.new(Fraction(1, 16), Pitch(4, "G")),
            Note.new(Fraction(1, 16), Pitch(4, "D")),
            Note.new(Fraction(1, 16), Pitch(4, "B")),
            Triplet(Pitch(4, "A"), Pitch(5, "C"), Pitch(4, "B")),
            Triplet(Pitch(4, "G"), Pitch(4, "E"), Pitch(4, "B")),
        ],
        Measure(
            [
                Note.new(Fraction(1, 8), Pitch(4, "A")),
                Note.new(Fraction(1, 8), Pitch(5, "C")),
                Grace(Pitch(5, "C"), Note.new(Fraction(1, 8), Pitch(4, "B"))),
                Note.new(Fraction(1, 8), Pitch(4, "A")),
                Note.new(Fraction(1, 8), Pitch(5, "D")),
                Grace(Pitch(4, "G"), Note.new(Fraction(1, 8), Pitch(4, "A"))),
            ],
            time=TimeSignature.new(3, 4),
        ),
        Measure(
            [
                # pentuplet
                Tuplet(
                    Pitch(5, "C"),
                    Grace(Pitch(5, "C"), Pitch(4, "B")),
                    Pitch(4, "G"),
                    Pitch(4, "E"),
                    Pitch(4, "B"),
                ),
                # slur onto the same note is a tie
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
                Note.new(Fraction(1, 8), Pitch(4, "A")),
                Note.new(Fraction(1, 8), Pitch(5, "C"), accent=Accent.SLUR),
            ],
            time=TimeSignature.new(4, 4),
        ),
        Measure(
            [
                Note.new(Fraction(1, 4), Pitch(5, "C"), accent=Accent.SLUR),
                # Ok so, the score I'm working off appears to be
                # mislabelled but to the best of my knowledge, the
                # second beat is:
                # a triplet
                # 3 pentuplets (with a grace note on the first)
                # a triplet (with a grace note)
                # But those 3 pentuplets must actually be a nested triplet?
                Triplet(
                    Pitch(5, "C"),
                    Triplet(
                        Grace(Pitch(5, "C"), Pitch(4, "B")),
                        Pitch(4, "G"),
                        Pitch(4, "B"),
                    ),
                    Grace(Pitch(5, "C"), Pitch(4, "B", FLAT)),
                ),
            ],
            time=TimeSignature.new(2, 4),
        ),
        Measure(
            [
                Triplet(
                    Pitch(4, "A"),
                    Grace(Pitch(5, "C"), Pitch(4, "B", FLAT)),
                    Pitch(4, "A"),
                ),
                Rest(Fraction(1, 8)),
                Note.new(Fraction(1, 16), Pitch(5, "C")),
                Rest(Fraction(1, 16)),
                Rest(Fraction(1, 4)),
            ],
            time=TimeSignature.new(3, 4),
        ),
        [
            Rest(Fraction(1, 4)),
            Rest(Fraction(1, 4)),
            Rest(Fraction(1, 8)),
            Note.new(Fraction(1, 8), Pitch(4, "C"), accent=Accent.SLUR),
        ],
        Measure(
            [
                Note.new(Fraction(1, 4), Pitch(5, "C")),
                Grace(Pitch(5, "C"), Note.new(Fraction(1, 16), Pitch(4, "B"))),
                Note.new(Fraction(1, 16), Pitch(4, "G")),
                Note.new(Fraction(1, 16), Pitch(4, "E")),
                Note.new(Fraction(1, 16), Pitch(4, "B")),
            ],
            time=TimeSignature.new(2, 4),
        ),
        Measure(
            [
                Note.new(Fraction(1, 8), Pitch(4, "A")),
                Note.new(Fraction(1, 8), Pitch(5, "C")),
                Grace(Pitch(5, "C"), Note.new(Fraction(1, 8), Pitch(4, "B"))),
                Note.new(Fraction(1, 8), Pitch(4, "A")),
                Note.new(Fraction(1, 8), Pitch(5, "D")),
                Grace(Pitch(4, "G"), Note.new(Fraction(1, 8), Pitch(4, "A"))),
            ],
            time=TimeSignature.new(3, 4),
        ),
        Measure(
            [
                Tuplet(
                    Pitch(5, "C"),
                    Grace(Pitch(5, "C"), Pitch(4, "B")),
                    Pitch(4, "G"),
                    Pitch(4, "E"),
                    Pitch(4, "B"),
                ),
                Note.new(Fraction(1, 4), Pitch(4, "A"), accent=Accent.SLUR),
            ],
            time=TimeSignature.new(2, 4),
        ),
        [Note.new(Fraction(1, 2), Pitch(4, "A"), accent=Accent.SLUR)],
        [Note.new(Fraction(1, 2), Pitch(4, "A"), accent=Accent.SLUR)],
        [Note.new(Fraction(1, 2), Pitch(4, "A"))],
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
                Note.new(Fraction(1, 2), Pitch(4, "G", FLAT)),
            ],
            time=TimeSignature.new(3, 4),
        ),
        Measure(
            [
                Tuplet(
                    Pitch(4, "F"),
                    Pitch(4, "D", SHARP),
                    Grace(Pitch(4, "F"), Pitch(4, "E")),
                    Pitch(4, "C"),
                    Grace(Pitch(4, "E"), Pitch(4, "D")),
                    Tone(Pitch(3, "B"), accent=Accent.SLUR),
                ),
                Note.new(Fraction(1, 8), Pitch(3, "B")),
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
                Note.new(Fraction(1, 4), Pitch(4, "C"), accent=Accent.SLUR),
                Triplet(
                    Pitch(4, "C"),
                    Tone(Pitch(4, "D"), accent=Accent.SLUR),
                    Tone(Pitch(4, "D"), accent=Accent.SLUR),
                ),
                Note.new(Fraction(1, 4), Pitch(4, "D"), accent=Accent.SLUR),
            ],
            time=TimeSignature.new(3, 4),
            accidentals={Fraction(0, 1): {"C": SHARP}},
        ),
        Measure(
            [
                Note.new(Fraction(1, 4), Pitch(4, "D")),
                Note.new(Fraction(1, 4), Pitch(4, "C"), accent=Accent.SLUR),
                Note.new(Fraction(1, 4), Pitch(4, "C"), accent=Accent.SLUR),
                Note.new(Fraction(1, 8), Pitch(4, "C")),
                Rest(Fraction(1, 8)),
            ],
            time=TimeSignature.new(4, 4),
            accidentals={Fraction(1, 4): {"C": SHARP}},
        ),
        Measure(
            [
                Note.new(
                    Fraction(3, 8), Chord(Pitch(3, "A", FLAT), Pitch(4, "D", FLAT))
                ),
                Note.new(
                    Fraction(1, 8),
                    Chord(Pitch(3, "G"), Pitch(4, "C")),
                    accent=Accent.SLUR,
                ),
            ],
            time=TimeSignature.new(2, 4),
        ),
        Measure(
            [
                Triplet(
                    Chord(Pitch(3, "G"), Pitch(4, "C")),
                    Tone(Chord(Pitch(3, "G", FLAT), Pitch(3, "B")), accent=Accent.SLUR),
                    Chord(Pitch(3, "G", FLAT), Pitch(3, "B")),
                ),
                Note.new(
                    Fraction(1, 4),
                    Chord(Pitch(3, "F"), Pitch(3, "B", FLAT)),
                    accent=Accent.SLUR,
                ),
                Triplet(
                    Chord(Pitch(3, "F"), Pitch(3, "B", FLAT)),
                    Chord(Pitch(3, "F", FLAT), Pitch(3, "B", DOUBLE_FLAT)),
                    Chord(Pitch(3, "E", FLAT), Pitch(3, "A", FLAT)),
                ),
            ],
            time=TimeSignature.new(3, 4),
        ),
        [
            Triplet(
                Chord(Pitch(3, "D"), Pitch(3, "G")),
                Chord(Pitch(3, "C", SHARP), Pitch(3, "F", SHARP)),
                Chord(Pitch(3, "C"), Pitch(3, "F")),
            ),
            Triplet(
                Chord(Pitch(2, "B"), Pitch(3, "E")),
                Chord(Pitch(2, "B", FLAT), Pitch(3, "E", FLAT)),
                Chord(Pitch(2, "A"), Pitch(3, "D")),
            ),
            Note.new(
                Fraction(1, 4),
                Chord(Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                accent=Accent.SLUR,
            ),
        ],
        Measure(
            [
                Note.new(
                    Fraction(1, 2),
                    Chord(Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                    accent=Accent.SLUR,
                )
            ],
            time=TimeSignature.new(2, 4),
        ),
        Measure(
            [
                Note.new(
                    Fraction(1, 4),
                    Chord(Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                    accent=Accent.SLUR,
                ),
                Triplet(
                    Chord(Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                    Chord(Pitch(2, "A"), Pitch(3, "D")),
                    Tone(
                        Chord(Pitch(2, "A", SHARP), Pitch(3, "D", SHARP)),
                        accent=Accent.SLUR,
                    ),
                ),
                Note.new(
                    Fraction(1, 8), Chord(Pitch(2, "A", SHARP), Pitch(3, "D", SHARP))
                ),
                Note.new(Fraction(1, 8), Chord(Pitch(2, "A"), Pitch(3, "D"))),
            ],
            time=TimeSignature.new(3, 4),
        ),
        Measure([], time=TimeSignature.new(2, 4)),
        Measure(
            [
                Note.new(Fraction(1, 8), Pitch(4, "C")),
                Note.new(Fraction(1, 8), Pitch(4, "F")),
                Triplet(
                    Grace(Pitch(4, "F"), Pitch(4, "D")),
                    Pitch(4, "C"),
                    Pitch(4, "F"),
                ),
            ],
            accidentals={Fraction(0, 1): {"C": SHARP, "D": SHARP, "F": SHARP}},
        ),
        Measure(
            [
                # Original score writes this as two triplets with bars
                # to denote the sextuplet notes
                Triplet(
                    Grace(Pitch(4, "F"), Pitch(4, "D")),
                    Pitch(4, "C"),
                    Tuplet(Pitch(4, "F"), None),
                ),
                Tuplet(
                    None,
                    None,  # this and above as triplet rest in score
                    Pitch(4, "G"),
                    Pitch(4, "D"),
                    Pitch(4, "F"),
                    Pitch(4, "C"),
                ),
            ],
            accidentals={
                Fraction(0, 1): {"C": SHARP, "D": SHARP, "F": SHARP, "G": SHARP}
            },
        ),
        [Note.new(Fraction(1, 2), Pitch(4, "D", SHARP))],
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
                Note.new(
                    Fraction(1, 2),
                    Chord(Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                    accent=Accent.SLUR,
                )
            ],
            time=TimeSignature.new(2, 4),
        ),
        [
            Note.new(
                Fraction(1, 2),
                Chord(Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                accent=Accent.SLUR,
            )
        ],
        [
            Note.new(
                Fraction(1, 2),
                Chord(Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)),
                accent=Accent.SLUR,
            )
        ],
        [Note.new(Fraction(1, 2), Chord(Pitch(2, "G", SHARP), Pitch(3, "C", SHARP)))],
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
