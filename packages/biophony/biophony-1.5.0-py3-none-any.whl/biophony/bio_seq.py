# ruff: noqa: D100
from .elem_seq import ElemSeq


class BioSeq:
    """
    Describe a biological sequence: ID, sequence, description.

    The class contains an ElemSeq object that contains the sequence, but also
    the sequence ID, if any, and an eventual description.

    :param seq: contains the elements of the sequence.
    :param seqid: the identifier.
    :param desc: a description.
    """

    def __init__(self, seq: ElemSeq, seqid: str = "", desc: str = "") -> None:
        """Object initialization."""
        self._seq = seq
        self._seqid = seqid
        self._desc = desc

    def __len__(self) -> int:
        """Return the sequence length."""
        return len(self._seq)

    @property
    def seqid(self) -> str:
        """
        Return the sequence ID.

        :return: the sequence ID.
        """
        return self._seqid

    @seqid.setter
    def seqid(self, value: str) -> None:
        """Set the sequence ID."""
        self._seqid = value

    @property
    def desc(self) -> str:
        """
        Return the description.

        :return: the description.
        """
        return self._desc

    @desc.setter
    def desc(self, value: str) -> None:
        self._desc = value

    @property
    def seq(self) -> ElemSeq:
        """
        Get the sequence.

        :return: the sequence.
        """
        return self._seq
