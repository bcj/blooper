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
from blooper.pitch import ARAB_SCALE, BOHLEN_PIERCE_SCALE, CHROMATIC_SCALE
from blooper.waveforms import WAVES

DEFAULT_TEMPO = Tempo.ALLEGRO
DEFAULT_DYNAMIC = Dynamic.from_name("mezzo-forte")
DEFAULT_KEY = None
DEFAULT_LOOPS = 1
DEFAULT_WAVE = "sine"
DEFAULT_PITCH = Pitch(4, "A")
DEFAULT_FREQUENCY = 440
DEFAULT_SCALE = CHROMATIC_SCALE


def main(input_args: Optional[list[str]] = None):
    """
    Run swim from the command line.
    """
    parser = ArgumentParser(description="Make bloops")
    commands = parser.add_subparsers(dest="command", required=True)

    sequencer = commands.add_parser("sequencer", help="A (very basic) step sequencer")
    sequencer.add_argument("path", type=Path, help="Where to save the output.")
    sequencer.add_argument(
        "--notes",
        action="append",
        required=True,
        nargs="+",
        type=parse_note,
        help="The notes to play",
    )
    sequencer.add_argument(
        "--tempo",
        action="append",
        type=int,
        help=f"How many beats (steps) to play in a minute. Defaults to {DEFAULT_TEMPO}",
    )
    sequencer.add_argument(
        "--dynamic",
        action="append",
        type=Dynamic.from_name,
        help="How loud the sequencer should play",
    )
    sequencer.add_argument(
        "-d",
        dest="dynamic",
        action="append",
        type=Dynamic.from_symbol,
        help="How loud the sequencer should play",
    )
    sequencer.add_argument(
        "--key",
        action="append",
        type=parse_key,
        help="The key to use",
    )
    sequencer.add_argument(
        "--loops",
        action="append",
        type=int,
        help="How many times to play through the sequenced notes",
    )
    sequencer.add_argument(
        "--wave",
        action="append",
        choices=WAVES.keys(),
        help=f"Kind of instrument to use. Defaults to {DEFAULT_WAVE}",
    )
    sequencer.add_argument(
        "--tuning-pitch",
        action="append",
        type=parse_pitch,
        help=f"The pitch to tune to. Defaults to {DEFAULT_PITCH}",
    )
    sequencer.add_argument(
        "--tuning-frequency",
        action="append",
        type=float,
        help=f"The frequency to tune to. Defaults to {DEFAULT_FREQUENCY}",
    )
    sequencer.add_argument(
        "--chromatic",
        dest="scale",
        action="append_const",
        const=CHROMATIC_SCALE,
        help="Use a chromatic scale (this is the default)",
    )
    sequencer.add_argument(
        "--arab",
        dest="scale",
        action="append_const",
        const=ARAB_SCALE,
        help="Use a Arab scale",
    )
    sequencer.add_argument(
        "--bohlen-pierce",
        dest="scale",
        action="append_const",
        const=BOHLEN_PIERCE_SCALE,
        help="Use a Bohlen-Pierce Scale",
    )

    args = parser.parse_args()

    if args.tempo is None:
        args.tempo = [DEFAULT_TEMPO]

    if args.dynamic is None:
        args.dynamic = [DEFAULT_DYNAMIC]

    if args.key is None:
        args.key = [DEFAULT_KEY]

    if args.loops is None:
        args.loops = [DEFAULT_LOOPS]

    if args.wave is None:
        args.wave = [DEFAULT_WAVE]

    if args.tuning_pitch is None:
        args.tuning_pitch = [DEFAULT_PITCH]

    if args.tuning_frequency is None:
        args.tuning_frequency = [DEFAULT_FREQUENCY]

    if args.scale is None:
        args.scale = [DEFAULT_SCALE]

    num_parts = len(args.notes)
    if num_parts:
        base_message = (
            "Each setting must be supplied either once, "
            "or once for each part being played. "
            "Invalid setting: {}"
        )

        if len(args.tempo) == 1:
            args.tempo *= num_parts
        elif len(args.tempo) != num_parts:
            raise ValueError(base_message.format("tempo"))

        if len(args.dynamic) == 1:
            args.dynamic *= num_parts
        elif len(args.dynamic) != num_parts:
            raise ValueError(base_message.format("dynamic"))

        if len(args.key) == 1:
            args.key *= num_parts
        elif len(args.key) != num_parts:
            raise ValueError(base_message.format("key"))

        if len(args.loops) == 1:
            args.loops *= num_parts
        elif len(args.loops) != num_parts:
            raise ValueError(base_message.format("loops"))

        if len(args.wave) == 1:
            args.wave *= num_parts
        elif len(args.wave) != num_parts:
            raise ValueError(base_message.format("wave"))

        if len(args.tuning_pitch) == 1:
            args.tuning_pitch *= num_parts
        elif len(args.tuning_pitch) != num_parts:
            raise ValueError(base_message.format("tuning pitch"))

        if len(args.tuning_frequency) == 1:
            args.tuning_frequency *= num_parts
        elif len(args.tuning_frequency) != num_parts:
            raise ValueError(base_message.format("tuning frequency"))

        if len(args.scale) == 1:
            args.scale *= num_parts
        elif len(args.scale) != num_parts:
            raise ValueError(base_message.format("scale"))

    inputs = []

    length = Fraction(1, 4)

    for index, pitches in enumerate(args.notes):
        total = 0
        notes: list[Note | Rest] = []
        for beats, pitch in pitches:
            duration = length * beats
            total += beats
            notes.append(Rest(duration) if pitch is None else Note(duration, pitch))

        inputs.append(
            (
                Synthesizer(
                    tuning=Tuning(
                        args.tuning_pitch[index],
                        args.tuning_frequency[index],
                        scale=args.scale[index],
                    ),
                    wave=args.wave[index],
                ),
                Part(
                    time=TimeSignature.new(total, 4),
                    tempo=args.tempo[index],
                    dynamic=args.dynamic[index],
                    measures=[notes] * args.loops[index],
                    key=args.key[index],
                ),
            )
        )

    record(args.path, Mixer.even(*inputs))


def parse_key(name: str) -> Key:
    original = name

    if name not in KEYS:
        name = " ".join(segment.capitalize() for segment in name.split(" "))

        if name not in KEYS:
            name = name.replace("b", "♭").replace("♮", "").replace("#", "♯")

    if name not in KEYS:
        raise ValueError(f"Unknown key: {original}")

    return KEYS[name]


def parse_note(text: str) -> tuple[int, Optional[Pitch]]:
    match = re.search(r"^(\d+)(.+?)$", text)
    if match:
        str_length, text = match.groups()
        length = int(str_length)
    else:
        length = 1

    return length, parse_pitch(text)


def parse_pitch(text: str) -> Optional[Pitch]:
    if text in ("", "-"):
        return None

    match = re.search(r"^([^\d]+?)(-?\d+)([^\d]*?)$", text)

    if not match:
        raise ValueError(f"Unknown note: {text}")

    pitch_class, order_string, accidental = match.groups()
    order = int(order_string)

    return Pitch.new(
        order,
        pitch_class.upper(),
        accidental or None,
    )


if __name__ == "__main__":
    main()
