# ruff: noqa: D100

# Standard
import copy
import random
import string

_PROGRAMS = {
        'bwa': {
            'opt': ["mem", "reference_genome.fasta", "reads_1.fastq",
                    "reads_2.fastq", ">", "output.sam"],
            },
        'bowtie': {
            'opt': ["index", "reference_genome", "output_index"],
            },
        'bowtie2': {
            'opt': ["-x", "reference_genome", "-1", "reads_1.fastq",
                    "-2", "reads_2.fastq", "-S", "output.sam"],
            },
        'samtools': {
            'opt': ["sort", "-o", "sorted_output.bam"],
            },
        'picard': {
            'opt': ["SortSam", "I=input.bam", "O=output.sorted.bam"],
            },
        'gatk': {
            'opt': ["SortSam", "I=input.bam", "O=output.sorted.bam"],
            },
        'STAR': {
            'opt': ["--genomeDir", "genome_index", "--readFilesIn",
                    "reads_1.fastq", "reads_2.fastq", "--outSAMtype", "SAM",
                    "--outFileNamePrefix", "output_"],
            },
        'hisat2': {
            'opt': ["-x", "reference_genome", "-1", "reads_1.fastq"],
            },
        'tophat': {
            'opt': ["-o", "output_dir", "genome_index", "reads_1.fastq",
                    "reads_2.fastq"],
            },
        'minimap2': {
            'opt': ["minimap2", "-ax", "sr", "reference_genome.fasta",
                    "reads.fastq", ">", "output.sam"],
            },
        }

def _quote(s: str) -> str:
    if " " in s or "\t" in s or "\n" in s:
        if '"' in s:
            s = s.replace('"', '\\"')
            s = f"'{s}'"
        else:
            s = s.replace("'", "\\'")
            s = f'"{s}"'
    return s

class ProgExec:
    """Description of a program execution used in a processing."""

    def __init__(self, _id: str, cmd: str, opt: list[str],
                 version: str) -> None:
        """Object initializer."""
        self._id = _id
        self._cmd = cmd
        self._opt = opt
        self._version = version

    @property
    def id(self) -> str:
        """Return the program ID."""
        return self._id

    @property
    def cmd(self) -> str:
        """Return the program command."""
        return self._cmd

    @property
    def opt(self) -> list[str]:
        """Return the program options."""
        return self._opt

    @property
    def cmd_line(self) -> str:
        """Return the program command line."""
        cmd = [self._cmd, *self._opt]
        return " ".join(_quote(c) for c in cmd)

    @property
    def version(self) -> str:
        """Return the program version."""
        return self._version

    @classmethod
    def create_random(cls) -> "ProgExec":
        """
        Create a random program execution instance.

        Returns:
            Program: A program with a random name and version.
        """

        cmd = random.choices(list(_PROGRAMS.keys()))[0]
        _id = f"{cmd}_" + ''.join(random.choices(string.digits, k=3))
        opt = copy.deepcopy(_PROGRAMS[cmd]['opt'])
        version = ''.join(random.choices(string.digits + string.ascii_letters,
                                         k=3))
        return cls(_id, cmd = cmd, opt = opt, version = version)

    @classmethod
    def create_random_list(cls, count: int) -> list["ProgExec"]:
        """
        Create a list of random program executions.

        Args:
            count (int): Number of program executions to create.

        Returns:
            list[Program]: List of random program executions.
        """
        return [cls.create_random() for _ in range(count)]
