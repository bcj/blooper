from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, Iterable


class SampleFile(ABC):
    """
    A file containing samples at a fixed rate
    """

    @property
    @abstractmethod
    def channels(self) -> int:
        """
        How many channels each channel contains
        """

    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """
        The Sample rate of the file.
        """

    @abstractmethod
    def load(
        self, sample_rate: int, volumes: Iterable[float], loop: bool = False
    ) -> Generator[tuple[float, ...], None, None]:
        """
        Load samples from a file with a compatible sample_rate.

        sample_rate: The sample rate that the files sample rate must be a
            multiple of.
        volumes: The envelope to use for the samples
        loop: Whether to loop to reach the full length of the envelope
        """

    @classmethod
    @abstractmethod
    def from_path(cls, path: Path) -> SampleFile:
        """
        Create a new SampleFile
        """


__all__ = ("SampleFile",)
