# ruff: noqa: D100

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

DEFAULT_RATE = 0.0
DEFAULT_SAMPLE = "Unknown"
TMP_PREFIX = "biophony"

@dataclass
class MutSimParams:
    """
    Class containing parameters to pass to the MutSim class.

    :param snp_rate: Probability of mutation at a single base.
    :param del_rate: Probability of deletion at a single base.
    :param ins_rate: Probability of insertion at a single base.
    :param sample_name: Sample name.
    """

    snp_rate: float = DEFAULT_RATE
    del_rate: float = DEFAULT_RATE
    ins_rate: float = DEFAULT_RATE
    sample_name: str = DEFAULT_SAMPLE


class MutSim:
    """
    Class for calling the command line script `mutation-simulator`.

    :param fasta_file: Input FASTA file to use. Set to "-" to read the file from stdin.
    :param vcf_file: Path to VCF file to generate. Set to "-" write the file to stdout.
    :param sim_params: Simulation parameters.
    """

    def __init__(self, fasta_file: str, vcf_file: str,
                 sim_params: MutSimParams | None = None) -> None:
        """Object initialization."""
        self._vcf_file = vcf_file
        self._sim_params = sim_params if sim_params else MutSimParams()
        self._fasta_file = fasta_file

    def run(self) -> None:
        """
        Run the simulator to generate a mutated VCF file.

        :raises RuntimeError: The call to `mutation-simulator` returned a
                              non-zero exit status.
        """
        with tempfile.TemporaryDirectory(prefix = TMP_PREFIX) as tmp_dir:

            # Prepare FASTA file
            if self._fasta_file == "-":
                fasta_file = Path(tmp_dir) / "seq.fasta"
                with fasta_file.open("w") as f:
                    for line in sys.stdin:
                        f.write(line)
            else:
                fasta_file = Path(self._fasta_file)

            # Get absolute path
            fasta_file = fasta_file.absolute()

            # Path/Basename for the output files (without file extension).
            out_base = Path(tmp_dir) / "variant"

            # Path to the generated VCF file.
            generated_vcf = Path(tmp_dir) / "variant_ms.vcf"

            cmd = ["mutation-simulator", "-q", "-o", str(out_base),
                   str(self._fasta_file),
                   "args", "-sn", str(self._sim_params.snp_rate),
                   "-de", str(self._sim_params.del_rate),
                   "-in", str(self._sim_params.ins_rate),
                   "-n", self._sim_params.sample_name]

            try:
                # Call mutation-simulator script
                subprocess.run(cmd, # noqa: S603
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.PIPE,
                               text=True,  # decode stderr as a string,
                                           # alias to `universal_newlines`
                               check=True, # raise CalledProcessError
                                           # when exit code != 1
                               )

                # Write to stdout if needed,
                # or move the generated VCF file to its expected output directory.
                if self._vcf_file == "-":
                    with generated_vcf.open("r") as f:
                        for line in f:
                            sys.stdout.write(line)
                else:
                    shutil.move(generated_vcf, self._vcf_file)

            except subprocess.CalledProcessError as e:
                raise RuntimeError(e.stderr) from None
