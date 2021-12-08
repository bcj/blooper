# Blooper

Blooper is a software synthesizer that reads music using a form of western musical notation (or at least a form that very roughly approximates it) and with support for customizable scale structure and tuning systems.

Mostly written as an exercise in learning music theory, it aims to make writing/playing music in western musical notation easy and music using other notations possible.

Update are likely to be rare and added functionality is more likely to focus on what is interesting to learn about than utility.
Not open source but have fun for personal use if you're not a corporation or a cop.

## Installation

Blooper requires Python 3.10.
It should run anywhere Python runs.

```sh
python setup.py install
```

## Usage

Blooper does not (yet) support importing music written/edited using a tool that is nice to use.

Blooper provides a (basic) [command-line sequencer](docs/cli.md), but for now, you will need to write music directly as code to access much of its functionality.

Writing music with Blooper requires interacting with more than a dozen distinct objects, so you may want to review the [project structure](docs/structure.md) before looking at [examples](docs/examples.md).
If you're trying to do anything especially complex, you may need to directly review the code.

Blooper renders all generated music to a WAV file.
It is unlikely to support other file formats any time soon and probably will never support live music generation.

## Contributing

Because this project is mostly made as a learning project, it is not currently accepting pull requests to add functionality.

Issues for any bugs you run into (especially platform-specific bugs) are appreciated, and where possible, will be fixed in a timely manner.

If you have recommendations on interesting ways to expand this project, feel free to submit the suggestion as an issue.