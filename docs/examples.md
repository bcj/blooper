# Examples

Each example can be run by running the file, passing it no arguments.
Each example will produce a `.wav` file with its same name.

## Minimal

[minimal.py](../examples/minimal.py) uses the bare-minimum number of imports required in order to produce music with Blooper (arguably one fewer than the bare-minimum as this track doesn't contain any rests).

## Rite

[rite.py](../examples/rite.py) is a (partial) conversion of a two piano arrangement of _The Rite of Spring_.
Blooper treats this as 4 parts as each hand is considered its own part.
This example shows off a bit more functionality of Blooper and also its limitations.
The original score is idiosyncratic enough—it is almost illegible as code.

# Sample

[sample.py](../examples/sample.py) provides an example of how to structure sample files for use with the Sampler.
Running this example will first generate a samples directory within the example folder.