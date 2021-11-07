"""
To install:

    python setup.py install
"""
from pathlib import Path
from typing import List

from setuptools import setup

from blooper.version import __version__

DIRECTORY = Path(__file__).parent
REQUIREMENTS = DIRECTORY / "requirements"


def read_requirements(path: Path) -> List[str]:
    with path.open("r") as stream:
        return [line for line in stream.read().splitlines() if line]


setup(
    name="blooper",
    description=("A software synth"),
    long_description=(DIRECTORY / "README.md").read_text("utf-8"),
    version=__version__,
    author="bcj",
    license=None,
    packages=("blooper",),
    entry_points={"console_scripts": ("blooper = blooper.cli:main",)},
    install_requires=read_requirements(REQUIREMENTS / "install.txt"),
    tests_require=read_requirements(REQUIREMENTS / "tests.txt"),
    classifiers=(
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Topic :: Artistic Software",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
    ),
)
