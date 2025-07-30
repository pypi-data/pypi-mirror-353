# ruff: noqa: D100

# Standard
import argparse
import sys

# First party
from .align_gen import AlignGen#, AlignFileFmt
from .sam_file import SamFile

def gen_sam(args: argparse.Namespace) -> None:
    """Run SAM Generator code."""

    align_gen = AlignGen(align_count = args.align_count,
                         pg_count = args.pg_count,
                         rg_count = args.rg_count,
                         platform = args.platform,
                         )
    sam_file = SamFile(align_gen)

    # Write
    if args.output == '-':
        sam_file.to_stream(sys.stdout)
    else:
        sam_file.to_file(args.output)

def add_gen_sam_subcmd(p: argparse.ArgumentParser) -> None:
    """Add subcommand gen-vcf."""
    p.set_defaults(func = gen_sam)

    # Output file
    o = p.add_argument_group("OUTPUT OPTIONS")
    o.add_argument("-o", "--output", default = "-",
                   help = ("Path to the file to generate."
                           'Set to "-" to use stdout.'))

    # Generation parameters
    g = p.add_argument_group("GENERATION OPTIONS")
    g.add_argument("-n", "--align-count", type = int, default = 10,
                   help = ("Number of alignment to generate."))
    g.add_argument("--pg-count", type = int, default = 3,
                   help = ("Number of program executions to generate."))
    g.add_argument("--platform", help = "Platform name.")
    g.add_argument("--rg-count", type = int, default = 1,
                   help = ("Number of read groups to generate."))
