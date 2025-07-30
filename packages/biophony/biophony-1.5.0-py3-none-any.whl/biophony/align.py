# ruff: noqa: D100

# Standard
import abc
import typing

# First party
from .prg import ProgExec
from .read_group import ReadGroup
from .align_seq_item import AlignSeqItem

class Alignment(abc.ABC):
    """Alignment main abstract class."""

    @property
    @abc.abstractmethod
    def programs(self) -> list[ProgExec]:
        """Return the list of programs."""
        msg = "programs property not implemented."
        raise NotImplementedError(msg)

    @property
    @abc.abstractmethod
    def read_groups(self) -> list[ReadGroup]:
        """Return the list of read groups."""
        msg = "read_groups property not implemented."
        raise NotImplementedError(msg)

    def __iter__(self) -> typing.Self:
        """
        Get the iterator on the sequences.

        :return: Itself as an iterator.
        """
        return self

    @abc.abstractmethod
    def __next__(self) -> AlignSeqItem:
        """
        Get the next sequence.

        :return: the next sequence.
        """
        msg = "__next__ method not implemented."
        raise NotImplementedError(msg)
