# ruff: noqa: D100

# Standard
import argparse
import pathlib
import sys
import typing

# First party
from .cov_gen import CovGen
from .range import str2range

def cov_writer(output: typing.TextIO, gen: CovGen) -> None:
    """Write coverage file."""

    for item in gen:
        print(item.to_cov_line(), file = output)

def gen_cov(args: argparse.Namespace) -> None:
    """Run Coverage Generator code."""

    # Generate
    gen = CovGen(
        chrom = args.chrom,
        pos_range = str2range(args.pos),
        depth_range = str2range(args.depth),
        depth_offset = args.depth_start,
        depth_change_rate = args.depth_change_rate,
    )

    # Output on stdin
    if args.output == "-":
        cov_writer(sys.stdout, gen)

    # file
    else:
        with pathlib.Path(args.output).open("w") as f:
            cov_writer(f, gen)

def add_gen_cov_subcmd(p: argparse.ArgumentParser) -> None:
    """Add subcommand gen-cov."""
    p.set_defaults(func = gen_cov)

    g = p.add_argument_group("GENERATION OPTIONS")
    g.add_argument("-c", "--chrom", dest = "chrom", type = str, default = "1",
                   help = ("The chromosome for which to generate a coverage"
                           " file."))
    g.add_argument("-p", "--pos", dest = "pos", type = str, default = "0-10000",
                   help = ("The positions to generate."
                         " Either a single value or a range begin-end"
                         ", where end is included."))
    g.add_argument("-d", "--depth", dest = "depth", type = str, default = "0",
                   help = ("The depth to generate. A single value or a range"
                         " start-stop, stop included."))
    g.add_argument("-r", "--depth-change-rate", dest = "depth_change_rate",
                   type = float, default = 0.0,
                   help = "Set depth change rate.")
    g.add_argument("-s", "--depth-start", dest = "depth_start", type = int,
                   default = "0",
                   help = ("The starting position from which depth will be"
                         " generated. Any position before this one will"
                         " get a depth of 0."))

    o = p.add_argument_group("OUTPUT OPTIONS")
    o.add_argument("-o", "--output", default = "-",
                   help = 'Path to output file. Set to "-" for stdout.')
