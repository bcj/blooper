from fractions import Fraction
from pathlib import Path

from blooper import Mixer, Note, Part, Pitch, Synthesizer, record

instrument = Synthesizer()
part = Part(
    [
        [
            Note.new(Fraction(1, 4), Pitch(4, "B")),
            Note.new(Fraction(1, 4), Pitch(4, "A")),
            Note.new(Fraction(1, 2), Pitch(4, "G")),
        ],
        [
            Note.new(Fraction(1, 4), Pitch(4, "B")),
            Note.new(Fraction(1, 4), Pitch(4, "A")),
            Note.new(Fraction(1, 2), Pitch(4, "G")),
        ],
        [
            Note.new(Fraction(1, 8), Pitch(4, "G")),
            Note.new(Fraction(1, 8), Pitch(4, "G")),
            Note.new(Fraction(1, 8), Pitch(4, "G")),
            Note.new(Fraction(1, 8), Pitch(4, "G")),
            Note.new(Fraction(1, 8), Pitch(4, "A")),
            Note.new(Fraction(1, 8), Pitch(4, "A")),
            Note.new(Fraction(1, 8), Pitch(4, "A")),
            Note.new(Fraction(1, 8), Pitch(4, "A")),
        ],
        [
            Note.new(Fraction(1, 4), Pitch(4, "B")),
            Note.new(Fraction(1, 4), Pitch(4, "A")),
            Note.new(Fraction(1, 2), Pitch(4, "G")),
        ],
    ]
)

record(Path("minimal.wav"), Mixer.solo(instrument, part))
