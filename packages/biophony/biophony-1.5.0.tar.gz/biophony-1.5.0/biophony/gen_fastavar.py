# ruff: noqa: D100

# Standard
import argparse
import pathlib
import sys
import typing

# First party
from .bio_seq_gen import BioSeqGen
from .bio_seq_var_gen import BioSeqVarGen
from .fasta_writer import FastaWriter
from .variant_maker import VariantMaker

def write_fastavar(output: typing.TextIO, seq_gen: BioSeqGen, var_maker: VariantMaker,
                   count: int) -> None:
    """Write Fasta variants file."""

    writer = FastaWriter(output = output, seq_line_len=80)

    for seq in seq_gen:
        writer.write_bio_seq(seq)
        var_gen = BioSeqVarGen(seq.seq, var_maker = var_maker,
                               count = count)
        for var in var_gen:
            writer.write_bio_seq(var)

def gen_fastavar(args: argparse.Namespace) -> None:
    """Run FASTA Variants Generator code."""

    var_maker = VariantMaker(ins_rate=args.ins_rate,
                             del_rate=args.del_rate,
                             mut_rate=args.mut_rate)

    seq_gen = BioSeqGen(seqlen=args.seq_len, count=args.nb_seq,
                        prefix_id="seq")

    # Stdout
    if args.output == "-":
        write_fastavar(sys.stdout, seq_gen = seq_gen, var_maker = var_maker,
                       count = args.nb_var)

    # File
    else:
        with pathlib.Path(args.output).open("w") as f: 
            write_fastavar(f, seq_gen = seq_gen, var_maker = var_maker,
                           count = args.nb_var)

def add_gen_fastavar_subcmd(p: argparse.ArgumentParser) -> None:
    """Add subcommand gen-fastavar."""
    p.set_defaults(func = gen_fastavar)

    g = p.add_argument_group("GENERATION OPTIONS")
    g.add_argument("--seq-length", dest="seq_len", default=60,
                   type=int,
                   help="The length of the sequences to generate.")
    g.add_argument("--nb-seq", dest="nb_seq", default=5, type=int,
                   help="The number of sequences to generate.")
    g.add_argument("--nb-var", dest="nb_var", default=1, type=int,
                   help=("The number of variants to generate for each"
                         " sequence."))
    g.add_argument("-m", "--mut-rate", "--snp-rate", dest="mut_rate",
                   type=float, default=0.0,
                   help="The probability of mutation of one base.")
    g.add_argument("-i", "--ins-rate", dest="ins_rate",
                   type=float, default=0.0,
                   help="The probability of insertion at one base.")
    g.add_argument("-d", "--del-rate", dest="del_rate",
                   type=float, default=0.0,
                   help="The probability of deletion of one base.")

    o = p.add_argument_group("OUTPUT OPTIONS")
    o.add_argument("-o", "--output", default = "-",
                   help = 'Path to output file. Set to "-" for stdout.')
