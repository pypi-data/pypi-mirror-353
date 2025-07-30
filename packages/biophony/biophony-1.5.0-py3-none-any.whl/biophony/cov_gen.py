# ruff: noqa: D100, S311

# Standard
import random

# First party
from .range import rand_range


class CovItem:
    """
    A coverage item corresponding to a line in a coverage file.

    :param chrom: The chromosome.
    :param pos:   The position.
    :param depth: The coverage depth.
    """

    def __init__(self, chrom: str, pos: int, depth: int) -> None:
        """Object initialization."""
        self._chrom = chrom
        self._pos = pos
        self._depth = depth

    @property
    def chrom(self) -> str:
        """Return the chromosome."""
        return f"chr{self._chrom}"

    @property
    def pos(self) -> int:
        """Return the position."""
        return self._pos

    @property
    def depth(self) -> int:
        """Return the depth."""
        return self._depth

    def __repr__(self) -> str:
        """Return a string representation of this object."""
        return ",".join((self.chrom, f"pos={self.pos}", f"depth={self.depth}"))

    def to_cov_line(self) -> str:
        """Export this item as coverage file line."""
        return "\t".join((self.chrom, str(self.pos), str(self.depth)))


class CovGen:
    """
    Generator of coverage items to write into a coverage file.

    :param chrom: Chromosome identifier.
    :param min_pos: Minimum position where coverage starts.
    :param max_pos: Maximum position where coverage ends.
    :param min_depth: Minimum depth of coverage allowed.
    :param max_depth: Maximum depth of coverage allowed.
    :param depth_offset: Position where coverage depth starts being generated.
    :param depth_change_rate: Probability of depth fluctuation at each position.
    """

    def __init__(self, chrom: str = "1",
                 pos_range: range = range(10000),
                 depth_range: range = range(0),
                 depth_offset: int = 0,
                 depth_change_rate: float = 0.0) -> None:
        """Object initialization."""
        self._chrom = chrom
        self._pos_range = pos_range
        self._depth_range = depth_range
        self._depth_offset = depth_offset
        self._depth_change_rate = depth_change_rate

        self._pos = -1
        self._depth: int | None = None

    def __iter__(self) -> "CovGen":
        """
        Get the iterator on the coverage items.

        :return: Itself as an iterator.
        """
        return self

    def __next__(self) -> CovItem:
        """
        Generate a coverage item.

        :return: A coverage item.
        """
        # Increase position
        if self._pos < 0:
            self._pos = self._pos_range.start
        else:
            self._pos += 1

        # Done
        if self._pos > self._pos_range.stop:
            raise StopIteration

        # Update depth
        if self._depth is None:
            if self._pos >= self._depth_offset:
                self._depth = rand_range(self._depth_range)
        elif (self._depth_change_rate > 0.0
              and random.random() <= self._depth_change_rate):
            self._depth += -1 if random.randint(0, 1) == 0 else +1
            self._depth = min(self._depth, self._depth_range.start)
            self._depth = max(self._depth, self._depth_range.stop)

        # Generate a new item
        return CovItem(self._chrom, self._pos,
                       0 if self._depth is None else self._depth)
