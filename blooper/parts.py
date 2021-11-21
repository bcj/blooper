"""
Definitions for a musical score that would be played by one or more
instruments and as written in western musical notation*

* But only kind of? This isn't being read from a musical staff and some
concepts are missing (e.g., Clefs). A measure just being a list of
notes and rests seems far from ideal. I guess a Measure class may appear
at some point if for no other reason than this current system doesn't
allow for polyphonics.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from fractions import Fraction
from functools import cache
from typing import Generator, Iterable, NamedTuple, Optional, cast

from blooper.notes import TAILOFF_FACTOR, Accent, Dynamic, Note, Rest, Tone
from blooper.pitch import FLAT, NATURAL, SHARP, Pitch, accidental_symbol


# TODO: Still not sure if this and Scale interact in the way we want.
# TODO: change to: name, root (pitch_class, accidental), accidentals
@dataclass(frozen=True)
class Key:
    """
    The sets of flats and sharps (or other accidentals) defining all
    pitch classes in a scale.

    Any unspecificed class is assumed to be natural.
    """

    root: str
    major: bool
    accidentals: dict[str, Fraction]

    @property
    def name(self) -> str:
        accidental = self.accidental(self.root)
        if accidental:
            root = f"{self.root}{accidental_symbol(accidental)}"
        else:
            root = self.root

        kind = "Major" if self.major else "Minor"

        return f"{root} {kind}"

    # needed so we can cache tone_to_step
    def __hash__(self) -> int:
        return hash((self.root, self.major, tuple(sorted(self.accidentals.items()))))

    @cache
    def accidental(self, pitch_class: str) -> Fraction:
        return self.accidentals.get(pitch_class, NATURAL)

    @cache
    def in_key(self, pitch: Pitch) -> Pitch:
        if pitch.accidental is None:
            return Pitch(
                pitch.order, pitch.pitch_class, self.accidental(pitch.pitch_class)
            )

        return pitch

    @classmethod
    def new(
        cls,
        root: str,
        major: bool,
        *,
        flats: Optional[Iterable[str]] = None,
        sharps: Optional[Iterable[str]] = None,
    ) -> Key:
        """
        Convenience method for creating keys.
        """

        accidentals = {}

        for pitch_classes, accidental in ((flats, FLAT), (sharps, SHARP)):
            if pitch_classes:

                for pitch_class in pitch_classes:
                    if pitch_class in accidentals:
                        raise ValueError(f"Pitch class specified twice: {pitch_class}")

                    accidentals[pitch_class] = accidental

        return cls(root, major, accidentals)


KEYS = {
    "C Major": Key.new("C", True),
    "G Major": Key.new("G", True, sharps=("F",)),
    "D Major": Key.new("D", True, sharps=("F", "C")),
    "A Major": Key.new("A", True, sharps=("C", "F", "G")),
    "E Major": Key.new("E", True, sharps=("F", "G", "C", "D")),
    "B Major": Key.new("B", True, sharps=("C", "D", "F", "G", "A")),
    "F♯ Major": Key.new("F", True, sharps=("F", "G", "A", "C", "D", "E")),
    "D♭ Major": Key.new("D", True, flats=("D", "E", "G", "A", "B")),
    "A♭ Major": Key.new("A", True, flats=("A", "B", "D", "E")),
    "E♭ Major": Key.new("E", True, flats=("E", "A", "B")),
    "B♭ Major": Key.new("B", True, flats=("B", "E")),
    "F Major": Key.new("F", True, flats=("B",)),
    "C Minor": Key.new("C", False, flats=("E", "A", "B")),
    "G Minor": Key.new("G", False, flats=("B", "E")),
    "D Minor": Key.new("D", False, flats=("B",)),
    "A Minor": Key.new("A", False),
    "E Minor": Key.new("E", False, sharps=("F",)),
    "B Minor": Key.new("B", False, sharps=("C", "F")),
    "F♯ Minor": Key.new("F", False, sharps=("F", "G", "C")),
    "C♯ Minor": Key.new("C", False, sharps=("C", "D", "F", "G")),
    "G♯ Minor": Key.new("G", False, sharps=("G", "A", "C", "D", "F")),
    "E♭ Minor": Key.new("E", False, flats=("E", "G", "A", "B", "C", "D")),
    "B♭ Minor": Key.new("B", False, flats=("B", "D", "E", "G", "A")),
    "F Minor": Key.new("F", False, flats=("A", "B", "D", "E")),
}


class TimeSignature(NamedTuple):
    beats_per_measure: int
    beat_size: Fraction

    @classmethod
    def new(cls, beats_per_measure: int, beat_size: int) -> TimeSignature:
        return TimeSignature(beats_per_measure, Fraction(1, beat_size))

    def __str__(self) -> str:
        return f"{self.beats_per_measure}/{self.beat_size.denominator}"


# These numbers have been somewhat arbitrarily chosen such that they
# conform to a list of ranges for each from wikipedia.
# It would be nice to eventually support the 'feel' that tempos imply
# when deciding how to shape notes. If that happens we probably will
# want to support variation within a range for each of these (or even
# without a range? You want largo to be fast—live your life).
# An alternative is to split tempo and feeling into separate ideas but
# provide convenience methods so if you say vivace that implies both
# Tempo.VIVACE and Feeling.VIVACE (also, you're totally going to try to
# call that other concept 'tone'. Remember that you can't)
class Tempo(IntEnum):
    """
    The speed to play a piece at (in BPM)
    """

    LARGHISSIMO = 20
    ADAGISSIMO = 25
    GRAVE = 45
    LARGO = 50
    LENTO = 60
    LARGHETO = 66
    ADAGIO = 70
    ADAGIETTO = 80
    ANDANTE = 85
    ANDANTINO = 90
    MODERATO = 100
    ANDANTE_MODERATO = 112
    ALLEGRETTO = 115
    ALLEGRO_MODERATO = 120
    ALLEGRO = 140
    VIVACE = 160
    VIVACISSIMO = 172
    ALLEGRISSIMO = 176
    PRESTO = 180
    PRESTISSIMO = 240


@dataclass
class State:
    time: TimeSignature
    tempo: int
    dynamic: Dynamic
    key: Optional[Key] = None
    tailoff_factor: Fraction = TAILOFF_FACTOR


class Measure:
    """
    A measure of music
    """

    def __init__(
        self,
        notes: Optional[Iterable[Note | Rest]] = None,
        *,
        time: Optional[TimeSignature] = None,
        tempos: Optional[dict[Fraction, int]] = None,
        dynamics: Optional[dict[Fraction, Dynamic]] = None,
        keys: Optional[dict[Fraction, Key]] = None,
    ):
        self.notes = list(notes) if notes else []
        self.time = time
        self.tempos = tempos or {}
        self.dynamics = dynamics or {}
        self.keys = keys or {}

    def length(self) -> Fraction:
        """
        The current length of the measure
        """
        return Fraction(sum(note.duration for note in self.notes))

    def add(
        self,
        note: Note | Rest,
        *,
        tempo: Optional[int] = None,
        dynamic: Optional[Dynamic] = None,
        key: Optional[Key] = None,
    ):
        """
        Add a note to the end of a measure, possibly including a tempo,
        dynamic, or key change.

        note: The note or rest being added
        tempo: A new tempo that starts at the beginning of the note.
        dynamic: A new dynamic that starts at the beginning of the note.
        key: A new key that starts at the beginning of the note.
        """
        if tempo or dynamic or key:
            position = self.length()

            if tempo:
                self.tempos[position] = tempo

            if dynamic:
                self.dynamics[position] = dynamic

            if key:
                self.keys[position] = key

        self.notes.append(note)

    @classmethod
    def _position(cls, time: TimeSignature, position: Fraction) -> str:
        """
        Provides a nice text representation of a position within a part.
        used for error messages.
        """
        beats = position // time.beat_size
        partial_beats = position % time.beat_size

        if partial_beats:
            return f"{beats} + {partial_beats}"

        return str(beats)

    def play(
        self,
        state: State,
        previous: Optional[Accent] = None,
    ) -> Iterable[Note | Rest]:
        """
        Iterate over all notes and rests in a measure, modifying the
        current state of the part being played
        """
        if self.time:
            state.time = self.time

        if state.key is None:
            state.key = KEYS["C Major"]

        measure_size = state.time.beat_size * state.time.beats_per_measure

        position = Fraction(0, 1)

        notes = self.notes
        length = self.length()
        if length > measure_size:
            raise ValueError(
                f"More notes than can fit in the measure ({length} > {measure_size})"
            )
        elif length < measure_size:
            notes = [*notes, Rest(measure_size - length)]

        tempo_changes = sorted(self.tempos.items())
        dynamic_changes = sorted(self.dynamics.items())
        key_changes = sorted(self.keys.items())

        count = len(notes)
        for index, note in enumerate(notes, 1):
            if tempo_changes:
                change_position = tempo_changes[0][0]
                if change_position < position:
                    raise ValueError(
                        f"Error at beat {self._position(state.time, change_position)}: "
                        "Tempo change mid-note. Use a tie."
                    )
                elif change_position == position:
                    state.tempo = tempo_changes.pop(0)[1]
                elif index == count:
                    raise ValueError(
                        f"Error at beat {self._position(state.time, change_position)}: "
                        "Tempo change after measure."
                    )

            if dynamic_changes:
                change_position = dynamic_changes[0][0]
                if change_position < position:
                    raise ValueError(
                        f"Error at beat {self._position(state.time, change_position)}: "
                        "Tempo change mid-note. Use a tie."
                    )
                elif change_position == position:
                    state.dynamic = dynamic_changes.pop(0)[1]
                elif index == count:
                    raise ValueError(
                        f"Error at beat {self._position(state.time, change_position)}: "
                        "Dynamic change after measure."
                    )

            if key_changes:
                change_position = key_changes[0][0]
                if change_position < position:
                    raise ValueError(
                        f"Error at beat {self._position(state.time, change_position)}: "
                        "Tempo change mid-note. Use a tie."
                    )
                elif change_position == position:
                    state.key = key_changes.pop(0)[1]
                elif index == count:
                    raise ValueError(
                        f"Error at beat {self._position(state.time, change_position)}: "
                        "Key change after measure."
                    )

            if isinstance(note, Note):
                if note.accent:
                    if state.time.beat_size < note.duration and not note.accent.long():
                        raise ValueError(
                            f"Error at beat {self._position(state.time, position)}: "
                            f"invalid accent for a long note: {note.accent}"
                        )

                    if not note.accent.can_follow(previous):
                        raise ValueError(
                            f"Error at beat {self._position(state.time, position)}: "
                            f"accent {note.accent} can not follow {previous}"
                        )

                duration, pitch, dynamic, accent = note.components(
                    state.time.beat_size, tailoff_factor=state.tailoff_factor
                )

                pitch = state.key.in_key(pitch)

                yield Note(duration, pitch, dynamic or state.dynamic, accent)

                if duration != note.duration:
                    yield Rest(note.duration - duration)

                position += note.duration
                previous = note.accent
            else:
                # we could catch slur-to-rest here but we can't catch
                # them between measures or at the end of a song so we
                # might as well leave them for elsewhere

                yield note
                position += note.duration
                previous = None


@dataclass(frozen=True)
class Part:
    """
    A collection of measures containing notes as well as the key and
    time signatures, dynamics, and their changes required to play those
    measures.

    NOTE: Polyphony is not currently supported on a per-part basis.
    """

    time: TimeSignature
    tempo: int
    dynamic: Dynamic
    measures: list[Measure | list[Note | Rest]]
    key: Optional[Key] = None
    _tailoff_factor: Fraction = TAILOFF_FACTOR

    def tones(
        self,
        sample_rate: int,
    ) -> Generator[tuple[int, Tone], None, None]:
        """
        Convert a part into a series of tones.

        Yields tuples containing the 0-indexed sample to start on, the
        tone to play.

        sample_rate: how many samples the recording will use for each second.
        """
        state = State(
            self.time, self.tempo, self.dynamic, self.key, self._tailoff_factor
        )

        previous_accent = None
        tied_index = 0
        tied_tone = None

        samples_per_minute = sample_rate * 60
        tempo = state.tempo
        samples_per_beat = round(samples_per_minute / tempo)

        index = 0
        for measure_index, measure in enumerate(self.measures):
            if not isinstance(measure, Measure):
                measure = Measure(measure)

            try:
                for note in measure.play(state, previous_accent):
                    if tempo != state.tempo:
                        tempo = state.tempo
                        samples_per_beat = round(samples_per_minute / tempo)

                    samples = round(
                        samples_per_beat
                        * state.time.beat_size.denominator
                        * note.duration
                    )

                    if isinstance(note, Rest):
                        if tied_tone is not None:
                            raise ValueError("Cannot slur/tie into a rest")

                        previous_accent = None
                    else:
                        tone = Tone(
                            samples,
                            note.pitch,
                            # We know measure is supplying the dynamic
                            cast(Dynamic, note.dynamic),
                            note.accent,
                        )

                        start_index = index
                        if tied_tone:
                            if tied_tone.pitch != tone.pitch:
                                # It was a slur not a tie
                                yield tied_index, tied_tone
                                tied_tone = None
                            else:
                                tone = Tone(
                                    tied_tone.duration + tone.duration,
                                    tone.pitch,
                                    # If there's a dynamic change over a tied
                                    # note we're currently ignoring it. sorry
                                    tied_tone.dynamic,
                                    tone.accent,
                                )
                                start_index = tied_index

                        if tone.accent == Accent.SLUR:
                            if tied_tone is None:
                                tied_index = index
                            tied_tone = tone
                        else:
                            tied_tone = None
                            yield start_index, tone

                        previous_accent = tone.accent

                    index += samples
            except Exception:
                # TODO: proper logging
                print(f"Error occured at measure {measure}:")
                raise

        if tied_tone:
            raise ValueError("Hanging slur/tie at end of part")


__all__ = ("KEYS", "Key", "Measure", "Part", "Tempo", "TimeSignature")
