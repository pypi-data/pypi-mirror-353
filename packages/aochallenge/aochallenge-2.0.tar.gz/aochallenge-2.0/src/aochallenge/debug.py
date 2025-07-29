#!/usr/bin/python3

from .grid import Grid2D, T
from .solver import Solver


def print_condensed(data: Grid2D[T]) -> None:
    for row in data:
        print(*row, sep="")


def print_csv(data: Grid2D[T]) -> None:
    for row in data:
        print(*row, sep=",")


def print_arranged(data: Grid2D[T]) -> None:
    col_widths: list[int] = []
    for r, row in enumerate(data):
        for c, value in enumerate(row):
            data_width = len(str(value))
            if c >= len(col_widths):
                col_widths.append(data_width)
            elif data_width > col_widths[c]:
                col_widths[c] = data_width
    for r, row in enumerate(data):
        for c, value in enumerate(row):
            if c:
                print(" ", end="")
            if type(value) == int:
                print(str(value).rjust(col_widths[c]), end="")
            else:
                print(str(value).ljust(col_widths[c]), end="")
        print("")


def print_solution(solution: Solver, *, indent: str = "") -> None:
    content = solution.__dict__
    for name, value in content.items():
        if name == "basename":
            continue
        print(f"{indent}{name}: {value}")
