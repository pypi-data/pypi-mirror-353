#!/usr/bin/python3

from PIL import Image
from typing import TypeAlias

from .grid import Grid2D, iter_grid, T

ColorLUT: TypeAlias = dict[T, int]


def save_image(filename: str, grid: Grid2D[T], colors: ColorLUT[T]) -> None:
    lut = {}
    width = len(grid[0])
    height = len(grid)
    img = Image.new("RGB", (width, height))
    px = img.load()  # type: ignore[func-returns-value]

    for k, c in colors.items():
        lut[k] = ((c >> 16) & 0xFF, (c >> 8) & 0xFF, c & 0xFF)

    for pos, v in iter_grid(grid):
        px[pos.x, pos.y] = lut[v]

    img.save(filename)
