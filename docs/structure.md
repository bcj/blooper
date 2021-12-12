# Structure

Blooper's structure is designed to mimic the structure used in Western music notation.
A work is created by writing one or more [part](#parts) in the style of sheet music and then assigning an [instrument](#instruments) to each part that is responsible for converting that part into sound.
[Recording](#recording) is handled by mixing together one or more instruments playing one or more parts.

## Parts

A `Part` (found in `blooper.parts`) operates like a piece of sheet music.
It contains the [tempo](#tempo), [time signature](#time-signatures) and [key signature](#key), as well as any number of [measures](#measures).

### Tempo

Tempos are supplied in beats per minute (bpm).
You can either supply an (integer) number directly, or with any of the named tempos in the `blooper.parts.Tempo` enum.

Parts default to `Tempo.ALLEGRO_MODERATO` (120 bpm).

### Time Signatures

A `TimeSignature` (found in `blooper.parts`) contains two values-the number of beats contained in a measure, and the length of a single beat (as a fraction of a whole note).
If you use the `new` classmethod, you can pass the beat length as its reciprocal.

The [`Part`](#parts) will softly enforce that every measure contains the correct number of beats.
Measure with too many beats will cause errors but measures with too few beats will be assumed to have rests for the remained of the beat.

Parts default to common time (4/4).

### Dynamic

A `Dynamic` (found in `blooper.notes`) represents the relative volume that notes should be played.
Dynamics can be supplied by name using the `from_name` method (e.g., `mezzo-piano`, `fortissimo`) or by symbol using the `from_symbol` method (e.g., `mp`, `ff`).

The Dynamic supplied with the [`Part`](#parts) will be used for all [`Note`s](#notes--rests) that do not supply their own dynamic.

Converting relative dynamics into output volumes is handled by the [`Instrument`](#instruments) playing the part.

Parts default to mezzo-forte.

### Key

A `Key` (found in `blooper.keys`) determines how to handle [notes](#notes--rests) in a [`Part`](#parts) that don't specify any accidentals.
The `blooper.keys.KEYS` dict specifies all the common major and minor keys.

If no key is supplied for a part, all notes will be treated as naturals unless specified otherwise.

### Measures

A `Measure` (found in `blooper.parts`) represents one set of [notes/rests](#notes--rests) as well as any [time](#time-signatures), [tempo](#tempo), [dynamic](#dynamic), and [key](#key) changes to introduce into a part and accidentals that only apply to the end of the measure.

All changes continue forward past the end of the measure (except for accidentals).
Time changes can only be intruded at the beginning of a Measure.
For all other changes, a fractional number of beats needs to be supplied to specify when they occur within the measure.
Accidentals will not apply to the next measure (including tied notes).

Changes are not allowed to occur in the middle of a note or rest.
If you want to specify a change partway through a note, you will need to split that note in two and use a [tie](#accents) to play those notes as one.
Ties are also required to stretch a note across a measure boundary.

If you do not need to specify any kind of change in a measure, you can supply measures to parts using a list instead of a Measure object.

#### Notes & Rests

A `Note` (found in `blooper.notes`) contains a duration (as a fractional number of beats) and a [tone](#tone).

You can skip creating a tone using the `Note.new` class method.

A `Rest` (also found in `blooper.notes`) only contains a duration.

##### Tone

A `Tone` (found in `blooper.notes`) consists of three components: a [pitch](#pitch) (or a [chord](#chord)), an optional [dynamic](#dynamic) (if not supplied, the part's current dynamic is used), and an optional [accent](#accents).

###### Pitch

A `Pitch` (found in `blooper.pitch`) contains three components: an order (you can read that as 'octave' for any common usage), a pitch class (i.e., the letters you refer to notes by), and an optional accidental (the fraction of a tone to offset the note by).

If an accidental isn't provided, the note will be interpreted by the [key](#key) the part is currently in.
You should use the constants `FLAT`/`NATURAL`/`SHARP` instead of rewriting fractions.

See [scales](#scales) if you're curious about some of the unusual wording choices when describing pitches.

###### Chord

A `Chord` (found in `blooper.pitch`) is a set of [pitches](#pitch) that are played in unison.

###### Accents

An `Accent` (found in `blooper.notes`) is a note modifier that affects how the instrument is supposed to approach playing a note.

Only `Accent.SLUR` and `Accent.TENUTO` are allowed on notes longer than the beat length specified in the [time signature](#time-signatures).
Likewise, these are the only accents allowed after a slurred/tied note.

You can use `Accent.SLUR` to tie multiple notes together (put the accent on every note being tied together except for the final one).

Is there an actual conceptual difference between a slur between two notes with the same pitch and a tie?
Please let me know.

##### Shorthand

Blooper provides a few convenience classes for writing groups of notes that tend to be treated specially in musical scores.

###### Grace Notes

A `Grace` (found in `blooper.notes`) provides a quick way to write grace notes without having to manually calculate how much the grace note takes from the note it precedes.

Grace takes a [pitch](#pitch)/[chord](#chord) or a [tone](#tone) for the grace note and a [note](#note--rest) for the note the grace note is associated with.

###### Triplets

A `Triplet` (found in `blooper.notes`) provides a quick way to write a trio of notes that each take 1/3 of a beat.
Triplet takes three values that are each either a [pitch](#pitch)/[chord](#chord) or [tone](#tone), or `None` for a rest.

A `Tuplet` (also found in `blooper.notes`) is like a triplet but splits a beat into an arbitrary number of notes (and/or rests).

[Grace Notes](#grace-notes), Triplets, and Tuplets can also be nested within Triplets/Tuplets.
See the [Rite of Spring example code](examples.md#rite) to see how this works.

## Instruments

Instruments take [parts](#parts) and optionally a [tuning](#tuning) and convert them into sound waves.
Presently, all parts are monophonic, but you can call an instrument's `play` method multiple times at once for polyphony.

Blooper implements two instruments: [Synthesizers](#synthesizers) and [Samplers](#samplers).
Both instruments allow you to specify an [envelope](#envelopes) and a [dynamic range](#dynamic-ranges).

### Synthesizers

A `Synthesizer` (found in `blooper.instruments`) is an instrument that plays notes by generating one of four types of wave: sine, square, triangle, or saw (i.e., saw-tooth).
It defaults to 'sine'.

### Samplers

A `Sampler` (found in `blooper.instruments`) is an instrument that plays notes by playing back prerecorded samples.

The sampler takes any number of samples.
Each is supplied along with a frequency and, optionally, a [dynamic range](#dynamic-ranges) in which to consider using that sample.

During playback the sampler will choose the closest matching sample.
If multiple samples are equidistant, the sampler will choose randomly.
The note is note played if the closest sample is too far away (maximum distance is given in [cents](https://en.wikipedia.org/wiki/Cent_(music)) and defaults to 1/5 of a semitone).

If samples are too short for the requested length they can either stop playing early or loop the sample.

Currently, the sampler requires samples to be `.wav` files with a sample rate that is a multiple of the output sample rate.

Blooper doesn't come with any of its own samples.

### Tuning

A `Tuning` (found in `blooper.pitch`) is used to map notes to frequencies.
A tuning takes a [pitch](#pitch) to tune, a frequency (in Hz) to tune that pitch to, and optionally a [scale](#scales) and [temperament](#temperaments).

Instruments all default to [concert pitch](https://en.wikipedia.org/wiki/Concert_pitch).

#### Scales

A `Scale` (found in `blooper.pitch`) defines the meaning of [pitches](#pitch) in a piece of music.
Tuning defaults to the 12-step [chromatic scale](https://en.wikipedia.org/wiki/Chromatic_scale) used by Western music.

A scale takes the number of steps in a cycle (a Western scale has 12 steps to an octave), a dict mapping indices to pitch classes (a Western scale has 'C' at 0 and 'B' at 11), a step size in fractions of a tone (a Western scale steps by semitones), and optionally a harmonic ratio representing the step between cycles (an octave has a value of 2).

When supplying notes for a part, each not must have a pitch class in the provided mapping and cannot have any accidentals with smaller offsets than the step size.

Blooper provides three scales by default: `CHROMATIC_SCALE` (a 12-tone Western Scale), `ARAB_SCALE` (a 24-tone quarter-tone step scale matching the 24-TET variant of the [Arab Tone System](https://en.wikipedia.org/wiki/Arab_tone_system)), and `BOHLEN_PIERCE_SCALE` (an implementation of the non-octaval [Bohlen-Pierce scale](https://en.wikipedia.org/wiki/Bohlen%E2%80%93Pierce_scale)).

#### Temperaments

A temperament is a list of multiplicative factors to use when applying the tuned frequency in a [tuning](#tuning) to any other note.

Tuning defaults to [equal temperament](https://en.wikipedia.org/wiki/Equal_temperament) and will automatically generate an equal temperament tuning for any scale you provide it.

It's recommended you stick with that for now.

#### Envelopes

Envelopes (found in `blooper.dynamics`) define how an instrument should shape each individual note.
Instruments default to `AttackDecaySustainRelease` (unsurprisingly, an [ADSR](https://en.wikipedia.org/wiki/Envelope_(music)#ADSR) envelope).

`AttackDecaySustainRelease` is user-configurable but you'll want to look at the code to see how each parameter is defined.

There is also a `Homogeneous` envelope that plays each note at a single volume.
Combining this with `Accent.TENUTO` may result in clipping.

#### Dynamic Ranges

A `DynamicRange` (in `blooper.dynamics`) specifies the softest and loudest an instrument should play.
The default dynamic range is between pianissimo (pp) and fortissississimo (ffff), with fortissimo (ff) defined as the loudest the instrument can play without risk of clipping.

## Recording

Recording is done with the `record` function (found in `blooper.wavs`).
It takes a path to save the recording to and a [mixer](#mixers), recording the output as a WAV file.

Currently, only mono and stereo recording is supported.

### Mixers

A `Mixer` (found in `blooper.mixers`) combines together one or more instrument, each playing one part, and combines it together as a single output.

The easiest way to use a mixer is to use `Mixer.solo` (providing an instrument and a part) if you have only one part or `Mixer.even` (supplying instrument, part tuples) if you have multiple instruments but you can also mix parts so different instruments play at different volumes.