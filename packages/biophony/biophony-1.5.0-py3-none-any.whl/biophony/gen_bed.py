# ruff: noqa: D100

# Standard
import argparse
import pathlib
import typing
import sys

# First party
from .bed_gen import BedGen
from .range import str2range

def bed_writer(output: typing.TextIO, gen: BedGen) -> None:
    """Write BED file."""

    for item in gen:
        print(item.to_bed_line(), file = output)

def gen_bed(args: argparse.Namespace) -> None:
    """Run BED Generator code."""
    gen = BedGen(
        chrom = args.chrom,
        pos_range = str2range(args.pos),
        chunk_range = str2range(args.chunk_range),
        hole_range = str2range(args.hole_range),
    )

    # Output on stdin
    if args.output == "-":
        bed_writer(sys.stdout, gen)

    # file
    else:
        with pathlib.Path(args.output).open("w") as f:
            bed_writer(f, gen)

def add_gen_bed_subcmd(p: argparse.ArgumentParser) -> None:
    """Add subcommand gen-cov."""
    p.set_defaults(func = gen_bed)

    g = p.add_argument_group("GENERATION OPTIONS")
    g.add_argument("-c", "--chrom", dest = "chrom", type = str, default = "1",
                   help = "The chromosome for which to generate a BED file.")
    g.add_argument("-p", "--pos", dest = "pos", type = str, default = "0-10000",
                   help = ("The positions to generate."
                         " Either a single value or a range begin-end"
                         ", where end is included."))
    g.add_argument("-C", "--chunk-range", dest = "chunk_range", type = str,
                   default = "200-500",
                   help = ("The range of the chunk sizes:  min-max."))
    g.add_argument("-H", "--hole-range", dest = "hole_range", type = str,
                   default = "0-100",
                   help = ("The range of the hole sizes:  min-max."
                           "A hole is placed between two chunks."))

    o = p.add_argument_group("OUTPUT OPTIONS")
    o.add_argument("-o", "--output", default = "-",
                   help = 'Path to output file. Set to "-" for stdout.')
