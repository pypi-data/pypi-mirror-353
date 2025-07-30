# ruff: noqa: D100

# First party
from .range import rand_range


class BedItem:
    """
    A BED item corresponding to a line in a BED file.

    :param chrom: The chromosome.
    :param range: The range of positions.
    """

    def __init__(self, chrom: str, pos_range: range) -> None:
        """Object initialization."""
        self._chrom = chrom
        self._pos_range = pos_range

    @property
    def chrom(self) -> str:
        """Return the chromosome."""
        return f"chr{self._chrom}"

    @property
    def pos_range(self) -> range:
        """Return the range of positions."""
        return self._pos_range

    @property
    def start(self) -> int:
        """Return the start position."""
        return self._pos_range.start

    @property
    def stop(self) -> int:
        """Return the stop position."""
        return self._pos_range.stop

    def __repr__(self) -> str:
        """Return a string representation of this object."""
        return ",".join((self.chrom, f"start={self.start}",
                         f"stop={self.stop}"))

    def to_bed_line(self) -> str:
        """Export this item as BED file line."""
        return "\t".join((self.chrom, str(self.start), str(self.stop)))

class BedGen:
    """
    Generator of BED items to write into a BED file.

    :param chrom: Chromosome identifier.
    :param pos_range: Coverage range.
    :param chunk_range: Chunk size range.
    :param hole_range: Hole size range.
    """

    def __init__(self, chrom: str = "1",
                 pos_range: range = range(10000),
                 chunk_range: range = range(200, 500),
                 hole_range: range = range(100)) -> None:
        """Object initialization."""
        self._chrom = chrom
        self._pos_range = pos_range
        self._chunk_range = chunk_range
        self._hole_range = hole_range

        self._pos = -1

    def __iter__(self) -> "BedGen":
        """
        Get the iterator on the BED items.

        :return: Itself as an iterator.
        """
        return self

    def __next__(self) -> BedItem:
        """
        Generate a BED item.

        :return: A BED item.
        """
        # Update position
        if self._pos < 0: # Start
            self._pos = self._pos_range.start

        # Make a hole
        else:
            self._pos += 1 + rand_range(self._hole_range)

        # Done
        if self._pos > self._pos_range.stop:
            raise StopIteration

        # Generate new item
        chunk_size = min(self._pos_range.stop - self._pos,
                         rand_range(self._chunk_range))
        item = BedItem(self._chrom, range(self._pos, self._pos + chunk_size))
        self._pos += chunk_size

        return item
