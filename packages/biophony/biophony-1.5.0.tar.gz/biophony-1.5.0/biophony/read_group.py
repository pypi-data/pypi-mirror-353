# ruff: noqa: D100

# Standard
import random
import string

_PLATFORMS = {
        "ILLUMINA": {
            "brand": "Illumina",
            "models": {
                "MiSeq": {
                    "seq_range": {"min": 150, "max": 300},
                    },
                "HiSeq": {
                    "seq_range": {"min": 150, "max": 300},
                    },
                "NextSeq": {
                    "seq_range": {"min": 150, "max": 300},
                    },
                "NovaSeq": {
                    "seq_range": {"min": 150, "max": 300},
                    },
                "iSeq": {
                    "seq_range": {"min": 150, "max": 300},
                    },
                },
            },
        "454": {
            "brand": "454",
            "models": {
                "GS FLX": {
                    "seq_range": {"min": 400, "max": 600},
                    },
                "GS Junior": {
                    "seq_range": {"min": 400, "max": 600},
                    },
                "GS FLX+": {
                    "seq_range": {"min": 400, "max": 600},
                    },
                },
            },
        "IONTORRENT": {
            "brand": "IonTorrent",
            "models": {
                "Ion Proton": {
                    "seq_range": {"min": 200, "max": 400},
                    },
                "Ion PGM": {
                    "seq_range": {"min": 200, "max": 400},
                    },
                "Ion S5": {
                    "seq_range": {"min": 200, "max": 400},
                    },
                },
            },
        "PACBIO": {
            "brand": "PacBio",
            "models": {
                "REVIO": {
                    "seq_range": {"min": 10000, "max": 20000},
                    },
                "RS": {
                    "seq_range": {"min": 10000, "max": 20000},
                    },
                "RS II": {
                    "seq_range": {"min": 10000, "max": 20000},
                    },
                "Sequel": {
                    "seq_range": {"min": 10000, "max": 20000},
                    },
                "Sequel II": {
                    "seq_range": {"min": 10000, "max": 20000},
                    },
                "Sequel IIe": {
                    "seq_range": {"min": 10000, "max": 20000},
                    },
                },
            },
        "Oxford": {
            "brand": "Oxford Nanopore",
            "models": {
                "MinION": {
                    "seq_range": {"min": 1000, "max": 30000},
                    },
                "GridION": {
                    "seq_range": {"min": 1000, "max": 30000},
                    },
                "PromethION": {
                    "seq_range": {"min": 1000, "max": 30000},
                    },
                },
            },
        "SOLID": {
            "brand": "Solid",
            "models": {
                "5500": {
                    "seq_range": {"min": 50, "max": 100},
                    },
                "5500XL": {
                    "seq_range": {"min": 50, "max": 100},
                    },
                },
            },
        "SANGER": {
            "brand": "Sanger",
            "models": {
                "ABI3730": {
                    "seq_range": {"min": 50, "max": 100},
                    },
                "ABI3730XL": {
                    "seq_range": {"min": 50, "max": 100},
                    },
                },
            },
        "HELICOS": {
            "brand": "Helicos",
            "models": {
                "HeliScope": {
                    "seq_range": {"min": 50, "max": 100},
                    },
                },
            },
        }

class ReadGroup:
    """Read group information."""

    def __init__(self,
                 _id: str,
                 sample: str,
                 library: str,
                 platform: str,
                 platform_unit: str,
                 description: str | None,
                 platform_model: str | None,
                 seq_len_min: int | None = None,
                 seq_len_max: int | None = None,
                 ) -> None:
        """
        Initialize a ReadGroup.

        Args:
            _id (str): Read group ID.
            sample (str): Sample name.
            library (str): Library name.
            platform (str): Platform name.
            platform_model (str): Platform model name.
            platform_unit (str): Platform unit name.
            description (str): Description of the read group.
            seq_len_min (int): Minimum sequence length.
            seq_len_max (int): Maximum sequence length.
        """
        self._id = _id
        self._sample = sample
        self._library = library
        self._platform = platform
        self._platform_model = platform_model
        self._platform_unit = platform_unit
        self._description = description
        self._seq_len_min = seq_len_min
        self._seq_len_max = seq_len_max

    @property
    def id(self) -> str:
        """Return the read group ID."""
        return self._id

    @property
    def sample(self) -> str:
        """Return the sample name."""
        return self._sample

    @property
    def library(self) -> str:
        """Return the library name."""
        return self._library

    @property
    def platform(self) -> str:
        """Return the platform name."""
        return self._platform

    @property
    def platform_model(self) -> str | None:
        """Return the platform model name."""
        return self._platform_model

    @property
    def platform_unit(self) -> str:
        """Return the platform unit name."""
        return self._platform_unit

    @property
    def description(self) -> str | None:
        """Return the read group description."""
        return self._description

    @property
    def seq_len_min(self) -> int:
        """Return the minimum sequence length."""
        return 10 if self._seq_len_min is None else self._seq_len_min

    @property
    def seq_len_max(self) -> int:
        """Return the maximum sequence length."""
        return 100 if self._seq_len_max is None else self._seq_len_max

    @classmethod
    def create_random(cls, platform: str | None = None) -> "ReadGroup":
        """
        Create a random read group instance.

        Returns:
            ReadGroup: A read group with a random ID and description.
        """
        kwargs = {}
        alphanum = string.ascii_letters + string.digits
        _id = ''.join(random.choices(alphanum, k = 8))
        sample = ''.join(random.choices(alphanum, k = 8))
        library = ''.join(random.choices(alphanum, k = 8))
        if platform is None:
            platform = random.choice(list(_PLATFORMS.keys()))
        x = _PLATFORMS[platform]
        if (isinstance(x, dict) and 'models' in x and isinstance(x['models'],
                                                                  dict)):
            platform_model: str = random.choice(list(x['models'].keys()))
            if 'seq_range' in x['models'][platform_model]:
                seq_range = x['models'][platform_model]['seq_range']
                if (isinstance(seq_range, dict) and 'min' in seq_range
                    and 'max' in seq_range):
                    kwargs['seq_len_min'] = seq_range['min']
                    kwargs['seq_len_max'] = seq_range['max']
        platform_unit = ''.join(random.choices(alphanum + '_', k = 23))
        description = ''.join(random.choices(alphanum + ':=;-_', k = 260))
        return cls(_id,
                   sample = sample,
                   library = library,
                   platform = platform,
                   platform_model = platform_model,
                   platform_unit = platform_unit,
                   description = description,
                   **kwargs,
                   )

    @classmethod
    def create_random_list(cls, count: int, # type: ignore[no-untyped-def]
                           **kwargs, # noqa: ANN003
                           ) -> list["ReadGroup"]:
        """
        Create a list of random read groups.

        Args:
            count (int): Number of read groups to create.
            kwargs: Additional arguments for read group creation.

        Returns:
            list[ReadGroup]: List of random read groups.
        """
        return [cls.create_random(**kwargs) for _ in range(count)]
