# ruff: noqa: D100

# Standard
import argparse

# First party
from .mutsim import DEFAULT_RATE, DEFAULT_SAMPLE, MutSim, MutSimParams


def gen_vcf(args: argparse.Namespace) -> None:
    """Run VCF Generator code."""
    params = MutSimParams(snp_rate=args.snp_rate,
                          del_rate = args.del_rate,
                          ins_rate = args.ins_rate,
                          sample_name = args.sample)

    mutsim = MutSim(fasta_file=args.fasta_file,
                    vcf_file = args.vcf_file,
                    sim_params = params)
    mutsim.run()

def add_gen_vcf_subcmd(p: argparse.ArgumentParser) -> None:
    """Add subcommand gen-vcf."""
    p.set_defaults(func = gen_vcf)

    # Input file
    i = p.add_argument_group("INPUT OPTIONS")
    i.add_argument("-f", "--fasta-file", dest="fasta_file", default="-",
                   help=("A FASTA file to use for generating the VCF file."
                         'Set to "-" to use stdin.'))

    # Output file
    o = p.add_argument_group("OUTPUT OPTIONS")
    o.add_argument("-o", "--output", "--output-vcf", dest="vcf_file",
                   default="-",
                   help=("Path to the VCF file to generate."
                         'Set to "-" to use stdout.'))

    # Generation parameters
    g = p.add_argument_group("GENERATION OPTIONS")
    g.add_argument("-m", "--snp-rate", dest="snp_rate", type=float,
                   default=DEFAULT_RATE,
                   help="The probability of mutation of one base.")
    g.add_argument("-i", "--ins-rate", dest="ins_rate", type=float,
                   default=DEFAULT_RATE,
                   help="The probability of insertion at one base.")
    g.add_argument("-d", "--del-rate", dest="del_rate", type=float,
                   default=DEFAULT_RATE,
                   help="The probability of deletion of one base.")
    g.add_argument("-s", "--sample", type=str,
                   default=DEFAULT_SAMPLE,
                   help="Sample name.")
