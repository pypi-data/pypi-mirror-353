# ruff: noqa: D100

# Standard
import collections.abc
import typing

# First party
from .elements import Elements


class ElemSeq(collections.abc.Iterable[str]):
    """Sequence of elements."""

    def __init__(self, seq: str) -> None:
        """Object initialization."""
        self._seq = seq
        self._n: int = 0  # Iterator index

    def __len__(self) -> int:
        """Return the sequence length."""
        return len(self._seq)

    @property
    def elements(self) -> Elements:
        """
        Return the weights of the elements.

        :return: The defined weights.
        """
        return Elements(self._seq)

    def __repr__(self) -> str:
        """Return a string representation of this object."""
        return self._seq

    def __iter__(self) -> typing.Iterator[str]:
        """Return an iterator on sequence elements."""
        return iter(self._seq)

    def __getitem__(self, val: int | slice) -> str:
        """Return an element of the sequence."""
        if isinstance(val, int):
            return self._seq[val]
        return self._seq[val.start:val.stop]

    def __eq__(self, other: object) -> bool:
        """Test equality with another sequence."""
        if not isinstance(other, str | ElemSeq):
            msg = "Equality test accepts only an ElemSeq object."
            raise TypeError(msg)
        i, j = iter(self), iter(other)
        while True:
            try:
                a = next(i)
            except StopIteration:
                a = None
            try:
                b = next(j)
            except StopIteration:
                b = None
            if a is None and b is None:
                return True
            if a != b:
                break
        return False
