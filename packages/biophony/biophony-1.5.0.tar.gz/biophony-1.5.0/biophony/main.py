# ruff: noqa: D100

# Standard
import argparse
import importlib.metadata
import random
import sys
import traceback
from pathlib import Path

# Third party
import rich_argparse

# First party
from .const import EPILOG
from .gen_bed import add_gen_bed_subcmd
from .gen_cov import add_gen_cov_subcmd
from .gen_fasta import add_gen_fasta_subcmd
from .gen_fastavar import add_gen_fastavar_subcmd
from .gen_fastq import add_gen_fastq_subcmd
from .gen_sam import add_gen_sam_subcmd
from .gen_vcf import add_gen_vcf_subcmd
from .logger import configure_logging, logger


class BiophonyFormatter(rich_argparse.RawTextRichHelpFormatter,
        rich_argparse.ArgumentDefaultsRichHelpFormatter):
    """Rich formatter for biophony."""

def read_args() -> argparse.Namespace:
    """Read command line arguments."""
    ver = importlib.metadata.version("biophony")
    parser = argparse.ArgumentParser(
            prog = "biophony",
            formatter_class = BiophonyFormatter,
            epilog = EPILOG,
            allow_abbrev = False,
            description = f"""biophony version {ver}.

biophony generates random genetic files for testing purposes.
""")

    # Main options
    parser.add_argument("--log-file", required = False,
                        help = "Path to a log file.")
    parser.add_argument("--quiet", "-q", action = "store_true",
                        help = "Set verbose level to 0.")
    parser.add_argument("--seed", "-s", type = int,
                        help = "Set the random seed.")
    parser.add_argument("--verbose", "-v", action = "count", dest = "verbose",
                        default = 1,
                        help = "Set verbose level.")
    parser.add_argument("--version", action = "store_true",
                        help = "Print the version number and exit.")

    # Add sub-commands
    subparsers = parser.add_subparsers(help = "Subcommands.")
    add_gen_bed_subcmd(subparsers.add_parser(
        "gen-bed",
        formatter_class = BiophonyFormatter,
        epilog = EPILOG,
        description = "Generate BED files."))
    add_gen_cov_subcmd(subparsers.add_parser(
        "gen-cov",
        formatter_class = BiophonyFormatter,
        epilog = EPILOG,
        description = "Generate coverage files."))
    add_gen_vcf_subcmd(subparsers.add_parser(
        "gen-vcf",
        formatter_class = BiophonyFormatter,
        epilog = EPILOG,
        description = "Generate VCF files."))
    add_gen_fasta_subcmd(subparsers.add_parser(
        "gen-fasta",
        formatter_class = BiophonyFormatter,
        epilog = EPILOG,
        description = "Generate FASTA files."))
    add_gen_fastavar_subcmd(subparsers.add_parser(
        "gen-fastavar",
        formatter_class = BiophonyFormatter,
        epilog = EPILOG,
        description = "Generate sequences and their variants as"
                      " FASTA files."))
    add_gen_fastq_subcmd(subparsers.add_parser(
        "gen-fastq",
        formatter_class = BiophonyFormatter,
        epilog = EPILOG,
        description = "Generate FASTQ files."))
    add_gen_sam_subcmd(subparsers.add_parser(
        "gen-sam",
        formatter_class = BiophonyFormatter,
        epilog = EPILOG,
        description = "Generate SAM files."))

    # Parse arguments
    args = parser.parse_args()

    # Print version
    if args.version:
        print(ver) # noqa: T201
        sys.exit(0)

    # Check verbosity & quiet
    if args.quiet:
        args.verbose = 0

    return args

def convert_argv_old_style() -> None:
    """Convert old style command line with gen-* commands."""
    # Get sub-command name and replace main command name
    cmd = Path(sys.argv[0])
    subcmd = cmd.name
    sys.argv[0] = str(cmd.parent / "biophony")

    # Extract main command options
    main_opts = {"-q": 0, "-v": 0, "--log-file": 1}
    found_main_opts: list[str] = []
    for opt, nb_values in main_opts.items():
        try:
            i = sys.argv.index(opt)
            found_main_opts += sys.argv[i:i + 1 + nb_values]
            sys.argv = sys.argv[:i] + sys.argv[i + 1 + nb_values:]
        except ValueError:
            pass

    # Insert sub-command and main options
    sys.argv = sys.argv[0:1] + found_main_opts + [subcmd] + sys.argv[1:]

def main_cli(*, old_style: bool = False) -> int:
    """Main entry point.""" # noqa: D401
    status: int = 0

    # Process old style command line
    if old_style:
        convert_argv_old_style()

    # Read commad line arguments
    args = read_args()

    # Set random seed
    if args.seed is not None:
        random.seed(args.seed) # Fixed seed
    else:
        random.seed() # Use system time

    # Configure logging
    configure_logging(args.verbose, args.log_file)
    logger.debug("Arguments: %s", args)

    try:
        args.func(args)

    except Exception as e:  # noqa: BLE001
        logger.debug(traceback.format_exc())
        logger.fatal("Exception occured: %s", e)
        status = 1

    return status

# DEPRECATED Old gen-cov script.
def gen_cov_cli() -> int:
    """Coverage file generation CLI."""
    return main_cli(old_style = True)

# DEPRECATED Old gen-vcf script.
def gen_vcf_cli() -> int:
    """VCF generation CLI."""
    return main_cli(old_style = True)

# DEPRECATED Old gen-fasta script.
def gen_fasta_cli() -> int:
    """FASTA generation CLI."""
    return main_cli(old_style = True)

# DEPRECATED Old gen-fastavar script.
def gen_fastavar_cli() -> int:
    """FASTA Variant generation CLI."""
    return main_cli(old_style = True)

# DEPRECATED Old gen-fastq script.
def gen_fastq_cli() -> int:
    """FASTQ Variant generation CLI."""
    return main_cli(old_style = True)
