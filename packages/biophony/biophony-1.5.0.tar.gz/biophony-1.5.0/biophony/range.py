# ruff: noqa: D100

# Standard
import random
import re

RANGE_RE = re.compile(r"^(?P<begin>[0-9]+)(-(?P<end>[0-9]+))?$")

def str2range(s: str) -> range:
    """Parse integer range."""
    m = RANGE_RE.search(s)
    if m:
        begin = int(m.group("begin"))
        end = begin if m.group("end") is None else int(m.group("end"))
    else:
        msg = f'Wrong range "{s}"pos.'
        raise ValueError(msg)

    return range(begin, end)

def rand_range(r: range) -> int:
    """Return a random integer inside a range."""
    return random.randint(r.start, r.stop)
