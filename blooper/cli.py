"""
Run blooper from the command line
"""
import re
from argparse import ArgumentParser
from fractions import Fraction
from pathlib import Path
from typing import Optional

from blooper import (
    KEYS,
    Dynamic,
    Key,
    Mixer,
    Note,
    Part,
    Pitch,
    Rest,
    Synthesizer,
    Tempo,
    TimeSignature,
    Tuning,
    record,
)
from blooper.waveforms import WAVES


def main(input_args: Optional[list[str]] = None):
    """
    Run swim from the command line.
    """
    parser = ArgumentParser(description="Make bloops")
    commands = parser.add_subparsers(dest="command", required=True)

    sequencer = commands.add_parser("sequencer", help="A (very basic) step sequencer")
    sequencer.add_argument("path", type=Path, help="Where to save the output.")
    sequencer.add_argument(
        "--tempo",
        type=int,
        default=Tempo.ALLEGRO,
        help="How many beats (steps) to play in a minute. Defaults to 140",
    )
    sequencer.add_argument(
        "--key",
        type=parse_key,
        # choices=KEYS.keys(),
        help="The key to use",
    )
    sequencer.add_argument(
        "--loops",
        type=int,
        default=1,
        help="How many times to play through the sequenced notes",
    )
    sequencer.add_argument(
        "--wave",
        default="sine",
        choices=WAVES.keys(),
        help="Kind of instrument to use",
    )
    sequencer.add_argument(
        "--tuning-pitch",
        type=parse_pitch,
        default=Pitch(4, "A"),
        help="The pitch to tune to",
    )
    sequencer.add_argument(
        "--tuning-frequency", type=float, default=440, help="The frequency to tune to"
    )
    sequencer.add_argument(
        "notes", nargs="+", type=parse_pitch, help="The notes to play"
    )

    args = parser.parse_args()

    length = Fraction(1, 4)
    notes: list[Note | Rest] = [
        Rest(length) if pitch is None else Note(length, pitch) for pitch in args.notes
    ]

    part = Part(
        TimeSignature.new(len(notes), 4),
        args.tempo,
        Dynamic.from_name("mezzo-forte"),
        [notes] * args.loops,
    )

    instrument = Synthesizer(
        Tuning(args.tuning_pitch, args.tuning_frequency), wave=args.wave
    )

    mixer = Mixer.solo(instrument, part)

    record(args.path, mixer)


def parse_key(name: str) -> Key:
    original = name

    if name not in KEYS:
        name = " ".join(segment.capitalize() for segment in name.split(" "))

        if name not in KEYS:
            name = name.replace("b", "♭").replace("♮", "").replace("#", "♯")

    if name not in KEYS:
        raise ValueError(f"Unknown key: {original}")

    return KEYS[name]


def parse_pitch(text: str) -> Optional[Pitch]:
    if text in ("", "-"):
        return None

    match = re.search(r"^([^\d]+)(\d+)([^\d]*)$", text)

    if not match:
        raise ValueError(f"Unknown note: {text}")

    pitch_class, order_string, accidental = match.groups()
    order = int(order_string)

    return Pitch.new(order, pitch_class.upper(), accidental or None)


if __name__ == "__main__":
    main()
