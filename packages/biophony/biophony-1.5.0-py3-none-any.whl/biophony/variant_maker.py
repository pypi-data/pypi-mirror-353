# ruff: noqa: D100

# First party
from .elem_seq import ElemSeq
from .elem_seq_var_gen import ElemSeqVarGen


class VariantMaker:
    """
    Generate variants.

    :param ins_rate: The insertion rate.
    :param del_rate: The deletion rate.
    :param mut_rate: The mutation rate.
    """

    def __init__(self, ins_rate: float = 0.0,
                 del_rate: float = 0.0, mut_rate: float = 0.0) -> None:
        """Object initialization."""
        self._del_rate = del_rate
        self._ins_rate = ins_rate
        self._mut_rate = mut_rate

        # Check that rates total <= 1.0
        if del_rate + ins_rate + mut_rate > 1.0:
            msg = "Total sum of rates must be <= 1.0."
            raise ValueError(msg)

    def make_elem_seq_var(self, seq: ElemSeq) -> ElemSeq:
        """
        Generate a variant.

        :param seq: The original sequence.

        :return: A variant.
        """
        gen = ElemSeqVarGen(seq=seq,
                            ins_rate=self._ins_rate,
                            del_rate=self._del_rate,
                            mut_rate=self._mut_rate)
        return next(gen)

    def __repr__(self) -> str:
        """Return a string representation of this object."""
        return (f"VariantMaker, ins_rate={self._ins_rate}"
                f", del_rate={self._del_rate}"
                f", mut_rate={self._mut_rate}.")
