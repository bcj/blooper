# Releases

## 1.0.0 (2021-12-12)

Initial working version

### Features

 *  Specify pitches using 'Scientific' Pitch Notation
     *  With full support for accidentals including arbitrarily large and microtonal accidentals.
 *  Customizable scales with support for adjusting the number of named pitch classes, pitch step size and the harmonic ratio (i.e., non-Octaval scales)
     *  The 12-tone chromatic scale, the 24-tone form of the Arab Tone System, and Bohlen-Pierce
 *  Adjustable tuning with support for providing your own temperament
     *  At present, all tuning is done relative to the first pitch class in a scale which may make just intonation impossible to tune to when performing in a key where the first pitch isn't that pitch class?
 *  Specify note lengths with Western Measural Notation
 *  Support for dynamics and accents on individual notes
     *  Accents currently supported: Accent, Marcato, Staccato, Staccatissimo, Tenuto, Slurs, Ties
 *  Specify musical parts with time, key, tempo, and dynamic changes
 *  Support for customizable instruments with adjustable dynamic ranges and note envelopes
     *  Synthesizers: support sine, square, triangle, and sawtooth waves
     *  Samplers: support for playing back samples from WAV files
 *  Polyphonics (both via multiple parts and by chording within parts)
 *  Writing to WAV files (in stereo or mono)