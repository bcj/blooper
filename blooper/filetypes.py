from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Iterable, Optional

from blooper.notes import Dynamic


@dataclass(frozen=True)
class UsageMetadata:
    """
    Metadata not contianed within a sample about the contexts it should
    be used.
    """

    # We're assuming the sample reflects a single pure or dominant tone.
    frequency: float  # in Hz

    # If supplied, only consider this sample compatible if it's within
    # this volume range.
    minimum_volume: Optional[Dynamic] = None
    maximum_volume: Optional[Dynamic] = None

    def compatible_dynamic(self, dynamic: Optional[Dynamic]) -> bool:
        """
        Check whether a sample is supposed to be played at a given
        dynamic.
        """
        if dynamic is not None:
            if self.minimum_volume and self.minimum_volume > dynamic:
                return False

            if self.maximum_volume and self.maximum_volume < dynamic:
                return False

        return True


class SampleFile(ABC):
    """
    A file containing samples at a fixed rate
    """

    @property
    @abstractmethod
    def usage_metadata(sel) -> UsageMetadata:
        """
        Usage metadata for the sample file
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
    def from_path(cls, path: Path, *, metadata: UsageMetadata) -> SampleFile:
        """
        Create a new SampleFile
        """


__all__ = ("SampleFile",)
