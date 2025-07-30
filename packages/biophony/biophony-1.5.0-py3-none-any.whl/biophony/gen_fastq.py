# ruff: noqa: D100

# Standard
import argparse
import gzip
import sys
from pathlib import Path

# First party
from .bio_read_gen import BioReadGen
from .elements import Elements
from .fastq_writer import FastqWriter


def check_args(args: argparse.Namespace) -> None:
    """Check arguments."""
    # Check output
    if args.gzip and args.output == "-":
        msg = ("Cannot output gzipped stream on stdout."
               " Please choose a valid file name.")
        raise ValueError(msg)

    # Parse quality range
    if len(args.quality) != 3 or args.quality[1] != "-": # noqa: PLR2004
        msg = ("The quality range must respect the format "
               "<first_char>-<last_char>.")
        raise ValueError(msg)
    if args.quality[0] > args.quality[2]:
        msg = ("In quality range, first character is greater"
               " than last character.")
        raise ValueError(msg)
    args.quality_range = (args.quality[0], args.quality[2])


def gen_fastq(args: argparse.Namespace) -> None:
    """Run FASTQ Generator code."""
    # Check arguments
    check_args(args)

    # Generate
    gen = BioReadGen(elements = Elements(args.elements),
                     quality = args.quality_range,
                     seqlen = args.length,
                     prefix_id = args.readid,
                     count = args.count)

    # Gzipped
    if args.gzip:
        with gzip.open(args.output, "wt", encoding="utf-8") as f:
            FastqWriter(f).write_reads(gen)

    # Plain output to stdout
    elif args.output == "-":
        FastqWriter(output=sys.stdout).write_reads(gen)

    # Plain output to File
    else:
        with Path(args.output).open("w") as f:
            FastqWriter(f).write_reads(gen)

def add_gen_fastq_subcmd(p: argparse.ArgumentParser) -> None:
    """Add subcommand gen-fastq."""
    p.set_defaults(func = gen_fastq)

    g = p.add_argument_group("GENERATION OPTIONS")
    g.add_argument("-c", "--count", dest="count", default=100, type=int,
                   help="The number of reads to generate.")
    g.add_argument("-n", "--length", dest="length", default=80, type=int,
                   help=("The length of the generated sequence in the"
                         " reads."))
    g.add_argument("-e", "--elements", dest="elements", default="ACTG",
                   help="The set of elements to use.")
    g.add_argument("-Q", "--quality", dest="quality", default="!-~",
                   help=("The range of quality characters to use, as"
                         "<first_char>-<last_char>."))
    g.add_argument("-r", "--readid", dest="readid", default="read",
                   help="THe prefix used to generated read IDs.")

    o = p.add_argument_group("OUTPUT OPTIONS")
    o.add_argument("-o", "--output", default="-",
                   help='Path to output file. Set to "-" for stdout.')
    o.add_argument("-z", "--gzip", action="store_true",
                   help="Generate gzipped output.")
