# ruff: noqa: D100

# Standard
import random
import string

# First party
from .elem_seq_gen import ElemSeqGen
from .read_group import ReadGroup

class AlignSeqItem:
    """Represents an alignment line in a SAM file."""

    def __init__(self,
                 rg: ReadGroup,
                 template_name: str,
                 seq: str,
                 qual: str | None = None,
                 ref_name: str | None = None,
                 pos: int | None = None,
                 mapping_quality: int | None = None,
                 ) -> None:
        """
        Initialize an AlignSeqItem.

        Args:
            rg (ReadGroup): Read group.
            template_name (str): Query template name.
            seq (str): Segment sequence.
            qual (str): ASCII of base quality.
            ref_name (str): Reference sequence name.
            pos (int): 1-based leftmost mapping position.
            mapping_quality (int): Mapping quality.
        """
        self._rg = rg
        self._template_name = template_name
        self._seq = seq
        self._qual = qual
        self._ref_name = ref_name
        self._pos = pos
        self._mapping_quality = mapping_quality

    @property
    def read_group(self) -> ReadGroup:
        """Return the read group."""
        return self._rg

    @property
    def mapped(self) -> bool:
        """Return True if the read is mapped."""
        return (self._ref_name is not None and self._pos is not None and
                self._pos > 0)

    @property
    def template_name(self) -> str:
        """Return the query template name."""
        return self._template_name

    @property
    def seq(self) -> str:
        """Return the segment sequence."""
        return self._seq
    
    @property
    def qual(self) -> str | None:
        """Return the ASCII of base quality."""
        return self._qual

    @property
    def ref_name(self) -> str | None:
        """Return the reference sequence name."""
        return self._ref_name

    @property
    def pos(self) -> int | None:
        """Return the 1-based leftmost mapping position."""
        return self._pos

    @property
    def mapping_quality(self) -> int | None:
        """Return the mapping quality."""
        return self._mapping_quality

    @classmethod
    def create_random(cls, seqlen: int, rg: ReadGroup) -> "AlignSeqItem":
        """
        Create a random AlignSeqItem.

        Returns:
            AlignSeqItem: A random AlignSeqItem object.
        """

        alphanum = string.ascii_letters + string.digits
        name =  ''.join(random.choices(alphanum + '_/', k = 16))

        # Create a random sequence
        seq = str(next(ElemSeqGen(seqlen)))
        qual = 'I' * len(seq)

        # Create an unmmapped alignment
        return cls(rg = rg, template_name = name, seq = seq, qual = qual)
