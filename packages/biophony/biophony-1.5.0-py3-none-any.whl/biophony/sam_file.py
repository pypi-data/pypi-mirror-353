# ruff: noqa: D100

# Standard
import typing
from pathlib import Path

# See https://samtools.github.io/hts-specs/SAMv1.pdf

# First party
from .align import Alignment

class SamFile:
    """SAM file."""

    def __init__(self, align: Alignment) -> None:
        """Object initializer."""
        self._align = align
        self._version = "1.6"

    def _write_header(self, f: typing.TextIO) -> None:
        """Write SAM header."""

        # Version
        f.write(f"@HD\tVN:{self._version}\tSO:unsorted\n")

        # Read groups
        for rg in self._align.read_groups:
            f.write(f"@RG\tID:{rg.id}\tSM:{rg.sample}\tLB:{rg.library}"
                    f"\tPL:{rg.platform}\tPM:{rg.platform_model}"
                    f"\tPU:{rg.platform_unit}"
                    f"\tDS:{rg.description}\n")

        # Programs
        for p in self._align.programs:
            f.write(f"@PG\tID:{p.id}\tPN:{p.cmd}\tCL:{p.cmd_line}"
                    f"\tVN:{p.version}\n")

        # Aligments
        for align in self._align:
            qname = align.template_name
            flag = 0
            rname = '*'
            pos = 0
            mapq = 255
            cigar = '*'
            rnext = '*'
            pnext = 0
            tlen = 0
            seq = align.seq
            qual = align.qual
            tags = f"RG:Z:{align.read_group.id}"
            if not align.mapped:
                flag |= 0x4
            f.write(f"{qname}\t{flag}\t{rname}\t{pos}\t{mapq}\t{cigar}"
                    f"\t{rnext}\t{pnext}\t{tlen}\t{seq}\t{qual}\t{tags}\n")

    def to_stream(self, stream: typing.TextIO) -> None:
        """Write SAM file."""
        self._write_header(stream)

    def to_file(self, file: Path) -> None:
        """Write SAM file."""

        with file.open("w") as f:
            self.to_stream(f)
