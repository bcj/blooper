# Command-Line Sequencer

Blooper provides a basic sequencer that you can run on the command line.
To run, pass the path to save the output to and any number of notes to play:

```bash
blooper sequencer a-minor.wav --notes A3 B3 C4 D4 E4 F4 G4 A4
```

Notes are written in the format `<length><pitch class><octave><accidental>`.
Rests are written with hyphens (`-`):

```bash
blooper sequencer clap-on-1-and-3.wav --notes b4 - b4 - a4 - a4
```

Notes and rests can be made longer by supplying an (integer) number of beats for them to span:

```bash
blooper sequencer quarter-half-whole.wav --notes a3 3- 2a3 2- 4a3
```

The duration of beats (in beats per minute) can be supplied by supplying the `--tempo` argument:

```bash
blooper sequencer largo.wav --tempo 50 --notes b4 a4 g4
```

Octave numbering defaults to `A4` being 440 Hz.
If you are used to midi's octave numbering you can adjust this by changing the tuning pitch:

```bash
blooper sequencer midi.wav --tuning-pitch a3 --notes b3 a3 g3
```

You can also change the tuning frequency:

```bash
blooper sequencer berlin.wav --tuning-frequency 443 --notes b4 a4 g4
```

You can supply accidentals after the octave to play sharps and flats:

```bash
blooper sequencer accidentals.wav --notes b4𝄫 b4bb b4♭ b4b b4♮ b4 b4# b4♯ b4## b4𝄪
```

Supported accidental symbols:

| Symbol |    Name      |     Modification      |
| -----: | :----------- | :-------------------- |
|      𝄫 | Double Flat  | 1 tone lower          |
|      ȸ | Sesquiflat   | 3 quartertones lower  |
|      ♭ | Flat         | 1 semitone lower      |
|      b | Flat         | 1 semitone lower      |
|      d | Demiflat     | 1 quartertone lower   |
|      ♮ | Natural      | 0 tones lower/higher  |
|      ‡ | Demisharp    | 1 quartertone higher  |
|      ♯ | Sharp        | 1 semitone higher     |
|      # | Sharp        | 1 semitone higher     |
|      ⩩ | Sesquisharp  | 3 quartertones higher |
|      𝄪 | Double Sharp | 3 quartertones higher |

The Unicode consortium _refuses_ to add symbols for quartertones so approximations were chosen.
Symbols can be repeated as long as the previous symbol modifies in the same direction (so `bbb`, `bbd` are allowed, `b#` and `db` are not).

You can also specify accidentals in words:

```bash
blooper sequencer accidentals.wav --notes b4double-flat b4flat b4natural b4sharp b4double-sharp
```

Supported accidental names:

|    Name      |     Modification      |
| :----------- | :-------------------- |
| `sesquiflat` | 3 quartertones lower  |
| `flat`       | 1 semitone lower      |
| `demiflat`   | 1 quartertone lower   |
| `natural`    | 0 tones lower/higher  |
| `demisharp`  | 1 quartertone higher  |
| `sharp`      | 1 semitone higher     |
| `Sesquisharp`| 3 quartertones higher |

Blooper also recognizes the multipliers `double` through `octuple` for modifying any of those accidentals.

You can specify a key with `--key` and notes without supplied accidentals will use the default symbol for that key:

```bash
blooper sequencer bflat-aflat-gnatural.wav --key "Ab Major" --notes b4 a4 g4
```

Blooper defaults to a [12-tone chromatic scale](https://en.wikipedia.org/wiki/Chromatic_scale).
To use quartertones, you will need to switch to the [24-tone Arab scale](https://en.wikipedia.org/wiki/Arab_tone_system).
Blooper also supports the [Bohlen-Pierce scale](https://en.wikipedia.org/wiki/Bohlen%E2%80%93Pierce_scale).
You can specify the scale to use by passing `--chromatic`, `--arab`, or `--bohlen-pierce`:

```bash
blooper sequencer quartertones.wav --arab --notes b4𝄫 b4ȸ b4♭ b4d b4♮ b4‡ b4♯ b4⩩ b4𝄪
```

```bash
blooper sequencer bp.wav --bohlen-pierce --notes b3 c4 j3 - b3 c4 j3 - b3 c4 j3
```

You can change the sound of the sequencer using `--wave`.
Supported waves are `sine` (the default), `square`, `triange`, and `saw`:

```bash
blooper sequencer square.wav --wave square --notes b4 a4 g4
```

You can change the volume of the instrument using the `--dynamic` argument to supply the volume by name:

```bash
blooper sequencer quiet.wav --dynamic piano --notes b4 a4 g4
```

```bash
blooper sequencer loud.wav --dynamic fortississimo --notes b4 a4 g4
```

Alternately, you can use `-d` to specify volume by symbol

```bash
blooper sequencer quieter.wav --d pp --notes b4 a4 g4
```

You can supply the `--loops` flag to play through the notes that many times in the recording

```bash
blooper sequencer twice.wav --loops 2 --notes b4 a4 g4 -
```

For polyphony, you can supply `--notes` multiple times.
For every flag other than `--notes`, you should either not supply it, supply it exactly once (to apply to each part), or once for each set of notes.

```bash
blooper sequencer poly.wav --key "A♭ Minor" --wave square --notes - a2 - b2 --loops 6 --wave sine --loops 1 --notes 2a3 2d4 2g4 2a4 2a3 2d4 2g4 a4 a3 d4 g4 a4 a4 a3 d4 g4 a4
```

There's absolutely nothing stopping you from having different parts in different keys or tempos or even different scales.
Have fun.