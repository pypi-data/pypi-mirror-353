# ruff: noqa: D100, S311

import random


class Elements:
    """
    Elements.

    ``{"A": 1, "C": 1, "T": 1, "G": 1}`` will generate a sequence with
    the same probability for all elements.
    ``{"A": 1, "C": 1, "T": 1, "G": 2}`` will generate a sequence with
    1/5 of A, 1/5 of C, 1/5 of T and 2/5 of G.
    """

    def __init__(self, elems: str = "ACTG") -> None:
        """Object initialization."""
        self._elems_str = elems
        self._elems: dict[str, int] = {}
        for e in elems:
            self._inc_weight(e)

    def __len__(self) -> int:
        """Return the number of elements."""
        return len(self._elems)

    def to_dict(self) -> dict[str, int]:
        """
        Export this object as a dictionary.

        :return: A dictionary whose keys are elements and values are the number
            of occurrences of each element (i.e.: its weight).
        """
        return self._elems.copy()

    def get_weight(self, elem: str) -> int:
        """
        Get the weight of one particular element.

        :param elem: The element.
        :return: The weight of this element.
        """
        return self._elems.get(elem, 0)

    def _inc_weight(self, elem: str, weight: int = 1) -> None:
        if elem in self._elems:
            self._elems[elem] += weight
        else:
            self._elems[elem] = weight

    def get_rand_elem(self, exclude: str = "", length: int = 1) -> str:
        """
        Generate random elements.

        Using the weights of the defined elements, randomly chooses elements
        and returns them.

        :param exclude: The element to exclude.
                Elements are concatenated together without separator. Example: "AT".
        :param length: The number of elements to generate.

        :return: A string containing the randomly selected elements,
            concatenated together without separator.
        """
        s = ""

        while len(s) != length:

            # Generate an element
            elem = None
            while elem is None:
                i = random.randint(0, len(self._elems_str) - 1)
                elem = self._elems_str[i]
                if elem in exclude:
                    elem = None

            # Append the element
            s += elem

        return s
