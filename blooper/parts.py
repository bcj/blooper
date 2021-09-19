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
from typing import Generator, Iterable, NamedTuple, Optional, Union

from blooper.notes import Accent, Dynamic, Note, Rest, Tone
from blooper.pitch import accidental_symbol


# TODO: Still not sure if this and Scale interact in the way we want.
# Major/Minor also seems presumptive
@dataclass(frozen=True)
class Key:
    """
    The sets of flats and sharps (or other accidentals) defining all
    pitch classes in a scale.

    Any unspecificed class is assumed to be natural.
    """

    tonic: str
    major: bool
    accidentals: dict[str, Fraction]

    @property
    def name(self) -> str:
        accidental = self.accidental(self.tonic)
        if accidental:
            tonic = f"{self.tonic}{accidental_symbol(accidental)}"
        else:
            tonic = self.tonic

        kind = "Major" if self.major else "Minor"

        return f"{tonic} {kind}"

    # needed so we can cache tone_to_step
    def __hash__(self) -> int:
        return hash((self.tonic, self.major, tuple(sorted(self.accidentals.items()))))

    @cache
    def accidental(self, pitch_class: str) -> Fraction:
        return self.accidentals.get(pitch_class, Fraction(0, 1))

    @classmethod
    def new(
        cls,
        tonic: str,
        major: bool,
        *,
        flats: Optional[Iterable[str]] = None,
        sharps: Optional[Iterable[str]] = None,
    ) -> Key:
        """
        Convenience method for creating keys.
        """

        accidentals = {}

        for pitch_classes, magnitude in ((flats, -1), (sharps, 1)):
            if pitch_classes:
                accidental = Fraction(magnitude, 2)

                for pitch_class in pitch_classes:
                    if pitch_class in accidentals:
                        raise ValueError(f"Pitch class specified twice: {pitch_class}")

                    accidentals[pitch_class] = accidental

        return cls(tonic, major, accidentals)


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
    beat_size: int  # actually a reciprical

    def __str__(self) -> str:
        return f"{self.beats_per_measure}/{self.beat_size}"


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


# TODO: This sure feels like a real mess still
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
    measures: list[list[Union[Note, Rest]]]
    key: Optional[Key] = None
    # dict key is 0-indexed measure number
    time_changes: Optional[dict[int, TimeSignature]] = None
    # outer key is 0-indexed measure number, inner key is measure offset:
    key_changes: Optional[dict[int, dict[Fraction, Key]]] = None
    tempo_changes: Optional[dict[int, dict[Fraction, int]]] = None
    dynamic_changes: Optional[dict[int, dict[Fraction, Dynamic]]] = None
    # This should eventually be rolled in with tempo as part of the mood
    # of the piece. As it is, this is a sort of hacky solution for
    # processing all temporal properties of accents prior to throwing
    # information about note size away when converting from notes to
    # durations. 0 / 1 will make all notes last the entirety of their
    # space (which is what tenuto and slur do regardless). This fraction
    # is how much to reduce the length of a standard note as a fraction
    # of the smaller of the note's length or the length of a standard
    # note (e.g., if the part is in X/4 time, any notes smaller than a
    # quarter note will be reduced by their length * this factor.
    # Larger notes like a whole note will only be reduces by the length
    # of a quarter note * this factor). Look, if you're actually
    # fiddling with this directly just scroll down to where this value
    # is used.
    _tailoff_factor: Fraction = Fraction(1, 4)

    # Where should this method actually live
    @classmethod
    def validate_accent(
        cls,
        note: Note,
        beat_size: Fraction,
        previous: Optional[Accent] = None,
    ):
        """
        Raise an error if a note has an accent that is not allowed.

        Only TENUTO/SLUR is allowed after a SLUR or if the note is
        longer than beat size.

        note: The note whos accent is beign checked
        previous: The accent of the previous note
        beat_size: The base beat size. If note supplied, will be
            calculated from starting time signature.
        """
        if note.accent:
            minimal = {Accent.TENUTO, Accent.SLUR}

            if previous == Accent.SLUR and note.accent not in minimal:
                raise ValueError(
                    f"Accent {note.accent.value} not allowed after a slur/tie"
                )

            if beat_size < note.duration and note.accent not in minimal:
                raise ValueError(
                    f"Accent {note.accent.value} not allowed on "
                    f"notes larget than the beat size ({beat_size})"
                )

    # This should move to the class that represents tone (as in feeling)
    def adjust_duration(self, note: Note, beat_size: Fraction) -> Note:
        """
        Replace a note with any accents modifying duration with a note
        of a new duration and without that accent.

        note: The note to adjust
        beat_size: How long a beat is.
        """
        duration = note.duration
        pitch = note.pitch
        dynamic = note.dynamic
        accent = note.accent
        regular_length = True

        if accent in (Accent.MARCATO, Accent.STACCATO):
            duration /= 2

            if accent == Accent.MARCATO:
                accent = Accent.ACCENT
            else:
                accent = None

            regular_length = False
        elif accent == Accent.STACCATISSIMO:
            duration /= 4
            accent = None
            regular_length = False
        elif accent == Accent.TENUTO:
            accent = None
            regular_length = False
        elif accent == Accent.SLUR:
            regular_length = False

        if regular_length:
            duration -= min(beat_size, duration) * self._tailoff_factor

        return Note(duration, pitch, dynamic, accent)

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

        time_changes = self.time_changes or {}
        tempo_changes = self.tempo_changes or {}
        dynamic_changes = self.dynamic_changes or {}

        beat_size = Fraction(1, self.time.beat_size)
        tempo = self.tempo
        dynamic = self.dynamic

        previous_accent = None
        tied_index = 0
        tied_tone = None

        samples_per_beat = round(sample_rate * 60 / tempo)

        index = 0
        for measure, notes in enumerate(self.measures):
            if measure in time_changes:
                beat_size = Fraction(1, time_changes[measure].beat_size)

            measure_tempo_changes = sorted(tempo_changes.get(measure, {}).items())
            measure_dynamic_changes = sorted(dynamic_changes.get(measure, {}).items())

            position = Fraction(0, 1)
            if measure_tempo_changes and measure_tempo_changes[0][0] == position:
                tempo = measure_tempo_changes.pop(0)[1]
                samples_per_beat = round(sample_rate * 60 / tempo)

            if measure_dynamic_changes and measure_dynamic_changes[0][0] == position:
                dynamic = measure_dynamic_changes.pop(0)[1]

            for note_or_rest in notes:
                try:
                    full_samples = samples = round(
                        samples_per_beat * beat_size.denominator * note_or_rest.duration
                    )

                    if isinstance(note_or_rest, Rest):
                        if tied_tone is not None:
                            raise ValueError("Cannot slur/tie into a rest")

                        previous_accent = None
                    else:
                        self.validate_accent(
                            note_or_rest, beat_size=beat_size, previous=previous_accent
                        )
                        note = self.adjust_duration(note_or_rest, beat_size)

                        if note.duration != note_or_rest.duration:
                            samples = round(
                                samples_per_beat * beat_size.denominator * note.duration
                            )

                        tone = Tone(
                            samples,
                            note.pitch,
                            note.dynamic or dynamic,
                            note.accent,
                        )

                        start_index = index
                        if tied_tone:
                            if tied_tone.pitch != note.pitch:
                                # It was a slur not a tie
                                yield tied_index, tied_tone
                                tied_tone = None
                            else:
                                tone = Tone(
                                    tied_tone.duration + tone.duration,
                                    tied_tone.pitch,
                                    tied_tone.dynamic,
                                    tone.accent,
                                )
                                start_index = tied_index

                        if note.accent == Accent.SLUR:
                            if tied_tone is None:
                                tied_index = index
                            tied_tone = tone
                        else:
                            tied_tone = None
                            yield start_index, tone

                        previous_accent = note.accent

                    position += note_or_rest.duration
                    index += full_samples

                    if measure_tempo_changes:
                        if measure_tempo_changes[0][0] < position:
                            raise ValueError(
                                f"Tempo change at {measure}: "
                                f"{measure_tempo_changes[0][0]} falls within a note"
                            )
                        elif measure_tempo_changes[0][0] == position:
                            tempo = measure_tempo_changes.pop(0)[1]
                            samples_per_beat = round(sample_rate * 60 / tempo)

                    if measure_dynamic_changes:
                        if measure_dynamic_changes[0][0] < position:
                            raise ValueError(
                                f"Dynamic change at {measure}: "
                                f"{measure_dynamic_changes[0][0]} falls within a note"
                            )
                        elif measure_dynamic_changes[0][0] == position:
                            dynamic = measure_dynamic_changes.pop(0)[1]

                except Exception:
                    # TODO: proper logging
                    print(f"Error occured at: {measure}: {position}")
                    raise

        if tied_tone:
            raise ValueError("Hanging slur/tie at end of part")


__all__ = ("KEYS", "Key", "Part", "Tempo", "TimeSignature")
