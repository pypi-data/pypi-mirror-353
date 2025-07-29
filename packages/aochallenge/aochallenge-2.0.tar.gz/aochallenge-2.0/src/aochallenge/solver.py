#!/usr/bin/python3

import sys
from typing import Any, Generator
from .input import load, variant


class Solver:
    def solve_more(self) -> Generator[int | str, None, None]:
        i: int = 1
        while hasattr(self, f"part{i}"):
            method = getattr(self, f"part{i}")
            yield method()
            i += 1

    def main(self) -> None:
        for i, result in enumerate(self.solve_more(), 1):
            print(f"{i}: {result}")

class Solution(Solver):
    basename: str # deprecated property!

    def __init__(self) -> None:
        self.basename: str = sys.argv[0][:-3]

#>    def solve_more(self) -> Generator[int | str, None, None]:
#>        i: int = 1
#>        while hasattr(self, f"part{i}"):
#>            method = getattr(self, f"part{i}")
#>            yield method()
#>            i += 1
#>
#>    def main(self) -> None:
#>        for i, result in enumerate(self.solve_more(), 1):
#>            print(f"{i}: {result}")
#>
    # Following legacy interface is deprecated

    def load(
        self,
        splitlines: bool = False,
        splitrecords: str | None = None,
        recordtype: list[type] | tuple[type, ...] | type | None = None,
        *,
        lut: dict[str | None, Any] | None = None,
    ) -> list[str | int | list[str | int]] | Any:
        basename: str = sys.argv[0][:-3]
        return load(
            splitlines,
            splitrecords,
            recordtype,
            lut=lut,
            filename = basename + "@@.input",
        )

    def variant(self) -> str | None:
        return variant()

    def print_condensed(self, data: list[list[int | str]]) -> None:
        from .debug import print_condensed

        return print_condensed(data)

    def print_csv(self, data: list[list[int | str]]) -> None:
        from .debug import print_csv

        return print_csv(data)

    def print_arranged(self, data: list[list[int | str]]) -> None:
        from .debug import print_arranged

        return print_arranged(data)
