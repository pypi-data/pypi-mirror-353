# ruff: noqa: D100

# Standard
import random

# First party
from .align import Alignment
from .prg import ProgExec
from .read_group import ReadGroup
from .align_seq_item import AlignSeqItem

class AlignGen(Alignment):
    """Alignment generator."""

    def __init__(self,
                 align_count: int = 10,
                 pg_count: int = 3,
                 rg_count: int = 1,
                 platform: str | None = None,
                 ) -> None:
        """
        Object initializer.

        This class generates random program executions and read groups
        for alignment files. It is a subclass of the Alignment class.

        Args:
            align_count (int): Number of alignments to generate.
            pg_count (int): Number of program executions to generate.
            rg_count (int): Number of read groups to generate.
            platform (str): Platform name.
        """
        super().__init__()
        self._align_count = align_count
        self._pg_count = pg_count
        self._rg_count = rg_count
        self._pgs: list[ProgExec] = []
        self._rgs: list[ReadGroup] = []
        self._platform = platform

        self._n = 0  # Current count of alignments
        self._rg_index = 0

    @property
    def programs(self) -> list[ProgExec]:
        """Return the list of programs."""
        if len(self._pgs) == 0:
            self._pgs = ProgExec.create_random_list(self._pg_count)
        return self._pgs

    @property
    def read_groups(self) -> list[ReadGroup]:
        """Return the list of read groups."""
        if len(self._rgs) == 0:
            kwargs = {}
            if self._platform is not None:
                kwargs['platform'] = self._platform
            self._rgs = ReadGroup.create_random_list(self._rg_count, **kwargs)
        return self._rgs

    def __next__(self) -> AlignSeqItem:
        """
        Get the next sequence.

        :return: the next sequence.
        """
        if self._n >= self._align_count:
            raise StopIteration
        self._n += 1
        if (self._rg_index < len(self._rgs) - 1 and
            self._n >= self._align_count // len(self._rgs)):
            self._rg_index += 1
        rg = self._rgs[self._rg_index]
        seqlen = random.randint(rg.seq_len_min, rg.seq_len_max)
        return AlignSeqItem.create_random(seqlen = seqlen, rg = rg)
