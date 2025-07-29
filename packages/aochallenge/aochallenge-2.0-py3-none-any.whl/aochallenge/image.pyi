from .grid import Grid2D as Grid2D, T as T, iter_grid as iter_grid
from typing import TypeAlias

ColorLUT: TypeAlias

def save_image(filename: str, grid: Grid2D[T], colors: ColorLUT[T]) -> None: ...
