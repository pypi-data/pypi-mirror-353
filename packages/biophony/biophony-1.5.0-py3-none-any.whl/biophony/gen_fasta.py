# ruff: noqa: D100

# Standard
import argparse
import gzip
import sys
from pathlib import Path

# First party
from .bio_seq_gen import BioSeqGen
from .elements import Elements
from .fasta_writer import FastaWriter


def gen_fasta(args: argparse.Namespace) -> None:
    """Run FASTA Generator code."""
    # Check output
    if args.gzip and args.output == "-":
        msg = ("Cannot output gzipped stream on stdout."
               " Please choose a valid file name.")
        raise ValueError(msg)

    gen = BioSeqGen(elements = Elements(args.elements),
                    seqlen = args.length, prefix_id = args.seqid)

    # Gzipped
    if args.gzip:
        with gzip.open(args.output, "wt", encoding = "utf-8") as f:
            FastaWriter(f, seq_line_len = args.line_size,
                        header = args.header).write_seqs(gen)

    # Plain output to stdout
    elif args.output == "-":
        FastaWriter(output = sys.stdout, seq_line_len = args.line_size,
                    header = args.header).write_seqs(gen)

    # Plain output File
    else:
        with Path(args.output).open("w") as f:
            FastaWriter(f, seq_line_len = args.line_size,
                        header = args.header).write_seqs(gen)


def add_gen_fasta_subcmd(p: argparse.ArgumentParser) -> None:
    """Add subcommand gen-fasta."""
    p.set_defaults(func = gen_fasta)

    g = p.add_argument_group("GENERATION OPTIONS")
    g.add_argument("-n", "--length", dest = "length", default = 1000,
                   type = int,
                   help = "The length of the generated sequence.")
    g.add_argument("--line-size", dest = "line_size", default = 80,
                   type = int,
                   help = "Maximum number of characters on each line.")
    g.add_argument("-e", "--elements", dest = "elements", default = "ACTG",
                   help = "The set of elements to use.")
    g.add_argument("-s", "--seqid", dest = "seqid", default = "chr",
                   help = "SeqID.")
    g.add_argument("-H", "--header", dest = "header",
                   action = argparse.BooleanOptionalAction,
                   help = ("Add generation metadata in the fasta file"
                         " header."))

    o = p.add_argument_group("OUTPUT OPTIONS")
    o.add_argument("-o", "--output", default = "-",
                   help = 'Path to output file. Set to "-" for stdout.')
    o.add_argument("-z", "--gzip", action = "store_true",
                   help = "Generate gzipped output.")
