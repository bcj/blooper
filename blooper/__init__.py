"""
A synthesizer/music generation tool
"""
from blooper.dynamics import AttackDecaySustainRelease, DynamicRange
from blooper.instruments import Sampler, Synthesizer
from blooper.keys import KEYS, Key
from blooper.mixers import Mixer
from blooper.notes import Accent, Dynamic, Note, Rest
from blooper.parts import COMMON_TIME, WALTZ_TIME, Measure, Part, Tempo, TimeSignature
from blooper.pitch import A440, FLAT, NATURAL, SHARP, Pitch, Scale, Tuning
from blooper.version import __version__
from blooper.wavs import record

__all__ = (
    "__version__",
    "A440",
    "COMMON_TIME",
    "FLAT",
    "KEYS",
    "NATURAL",
    "SHARP",
    "WALTZ_TIME",
    "Accent",
    "AttackDecaySustainRelease",
    "Dynamic",
    "DynamicRange",
    "Key",
    "Measure",
    "Mixer",
    "Note",
    "Part",
    "Pitch",
    "Rest",
    "Sampler",
    "Scale",
    "Synthesizer",
    "Tempo",
    "TimeSignature",
    "Tuning",
    "record",
)
