#!/usr/bin/python3

from __future__ import annotations
import itertools
from typing import cast, Iterator, NamedTuple, Self, TypeAlias, TypeVar


# Note, that we use "type: ignore[override]", because we override the default
# types of NamedTuple operators
class Coord2D(NamedTuple):
    x: int
    y: int

    def __add__(self, other: Coord2D | tuple[int, int] | int) -> Coord2D:  # type: ignore[override]
        # Note: NamedTuple has an __add__ method defined with different annotation
        if isinstance(other, Coord2D):
            return Coord2D(self.x + other.x, self.y + other.y)
        if isinstance(other, tuple) and len(other) == 2:
            return Coord2D(self.x + other[0], self.y + other[1])
        if isinstance(other, int):
            return Coord2D(self.x + other, self.y + other)
        return NotImplemented

    def __sub__(self, other: Coord2D | tuple[int, int] | int) -> Coord2D:
        if isinstance(other, Coord2D):
            return Coord2D(self.x - other.x, self.y - other.y)
        if isinstance(other, tuple) and len(other) == 2:
            return Coord2D(self.x - other[0], self.y - other[1])
        if isinstance(other, int):
            return Coord2D(self.x - other, self.y - other)
        return NotImplemented


class Coord3D(NamedTuple):
    x: int
    y: int
    z: int

    def __add__(self, other: Coord3D | tuple[int, int, int] | int) -> Coord3D:  # type: ignore[override]
        # Note: NamedTuple has an __add__ method defined with different annotation
        if isinstance(other, Coord3D):
            return Coord3D(self.x + other.x, self.y + other.y, self.z + other.z)
        if isinstance(other, tuple) and len(other) == 3:
            return Coord3D(self.x + other[0], self.y + other[1], self.z + other[2])
        if isinstance(other, int):
            return Coord3D(self.x + other, self.y + other, self.z + other)
        return NotImplemented

    def __sub__(self, other: Coord3D | tuple[int, int, int] | int) -> Coord3D:
        if isinstance(other, Coord3D):
            return Coord3D(self.x - other.x, self.y - other.y, self.z - other.z)
        if isinstance(other, tuple) and len(other) == 3:
            return Coord3D(self.x - other[0], self.y - other[1], self.z - other[2])
        if isinstance(other, int):
            return Coord3D(self.x - other, self.y - other, self.z - other)
        return NotImplemented


_Coord2D = Coord2D | tuple[int, int]
_Coord3D = Coord3D | tuple[int, int, int]


def manhattan_2d(a: _Coord2D, b: _Coord2D) -> int:
    d = _c2d(a) - b
    return abs(d.x) + abs(d.y)


def manhattan_3d(a: _Coord3D, b: _Coord3D) -> int:
    d = _c3d(a) - b
    return abs(d.x) + abs(d.y) + abs(d.z)


def is_within_2d(coord: _Coord2D, corner1: _Coord2D, corner2: _Coord2D) -> bool:
    v = _c2d(coord)
    c1 = _c2d(corner1)
    c2 = _c2d(corner2)
    return v.x >= c1.x and v.y >= c1.y and v.x <= c2.x and v.y <= c2.y


def is_within_3d(coord: _Coord3D, corner1: _Coord3D, corner2: _Coord3D) -> bool:
    v = _c3d(coord)
    c1 = _c3d(corner1)
    c2 = _c3d(corner2)
    return (
        v.x >= c1.x
        and v.y >= c1.y
        and v.z >= c1.z
        and v.x <= c2.x
        and v.y <= c2.y
        and v.z <= c2.z
    )


def neighbors_2d(coord: _Coord2D) -> list[Coord2D]:
    return [d + coord for d in _neighbor_direct_2d]


def bounded_neighbors_2d(
    coord: _Coord2D, corner1: _Coord2D, corner2: _Coord2D
) -> list[Coord2D]:
    return [
        d + coord
        for d in _neighbor_direct_2d
        if is_within_2d(d + coord, corner1, corner2)
    ]


def neighbors_full_2d(coord: _Coord2D) -> list[Coord2D]:
    return [d + coord for d in _neighbor_corner_2d]


def bounded_neighbors_full_2d(
    coord: _Coord2D, corner1: _Coord2D, corner2: _Coord2D
) -> list[Coord2D]:
    return [
        d + coord
        for d in _neighbor_corner_2d
        if is_within_2d(d + coord, corner1, corner2)
    ]


def neighbors_3d(coord: _Coord3D) -> list[Coord3D]:
    return [d + coord for d in _neighbor_direct_3d]


def bounded_neighbors_3d(
    coord: _Coord3D, corner1: _Coord3D, corner2: _Coord3D
) -> list[Coord3D]:
    return [
        d + coord
        for d in _neighbor_direct_3d
        if is_within_3d(d + coord, corner1, corner2)
    ]


def neighbors_edge_3d(coord: _Coord3D) -> list[Coord3D]:
    return [d + coord for d in _neighbor_edge_3d]


def bounded_neighbors_edge_3d(
    coord: _Coord3D, corner1: _Coord3D, corner2: _Coord3D
) -> list[Coord3D]:
    return [
        d + coord
        for d in _neighbor_edge_3d
        if is_within_3d(d + coord, corner1, corner2)
    ]


def neighbors_full_3d(coord: _Coord3D) -> list[Coord3D]:
    return [d + coord for d in _neighbor_corner_3d]


def bounded_neighbors_full_3d(
    coord: _Coord3D, corner1: _Coord3D, corner2: _Coord3D
) -> list[Coord3D]:
    return [
        d + coord
        for d in _neighbor_corner_3d
        if is_within_3d(d + coord, corner1, corner2)
    ]


########## Grids ####################

T = TypeVar("T")

# from Python 3.12 (mypy is also not prepared for this, yet)
# type MutableGrid2D[T] = list[list[T]]
# type _ImmutableDim[T] = tuple[T, ...]|str
# type _ImmutableGrid2D[T] = tuple[_immutableDim[T], ...]|list[_immutableDim[T]]
# type Grid2D[T] = MutableGrid2D[T]|_ImmutableGrid2D[T]
# type MutableGrid3D[T] = list[list[list[T]]]
# type _ImmutableGrid23[T] = tuple[_immutableGrid2D[T], ...]|list[_immutableGrid2D[T]]
# type Grid3D[T] = MutableGrid3D[T]|_ImmutableGrid3D[T]

MutableGrid2D: TypeAlias = list[list[T]]
Grid2D: TypeAlias = list[list[T]] | tuple[tuple[T, ...], ...]
MutableGrid3D: TypeAlias = list[list[list[T]]]
Grid3D: TypeAlias = list[list[list[T]]] | tuple[tuple[tuple[T, ...], ...], ...]


def create_grid_2d(size: _Coord2D | Grid2D[T], default: T) -> Grid2D[T]:
    if not isinstance(size[0], int):
        coord = cast(Grid2D[T], size)
        size = dimensions_2d(coord)
    size = _c2d(cast(Coord2D, size))
    grid = [[default] * size.x for _ in range(size.y)]
    return grid


def create_grid_3d(size: _Coord3D | Grid3D[T], default: T) -> Grid3D[T]:
    if not isinstance(size[0], int):
        coord = cast(Grid3D[T], size)
        size = dimensions_3d(coord)
    size = _c3d(cast(Coord3D, size))
    grid = [[[default] * size.x for _1 in range(size.y)] for _2 in range(size.z)]
    return grid


def width_2d(grid: Grid2D[T]) -> int:
    return len(grid[0])


def height_2d(grid: Grid2D[T]) -> int:
    return len(grid)


def width_3d(grid: Grid3D[T]) -> int:
    return len(grid[0][0])


def height_3d(grid: Grid3D[T]) -> int:
    return len(grid[0])


def depth_3d(grid: Grid3D[T]) -> int:
    return len(grid)


def dimensions_2d(grid: Grid2D[T]) -> Coord2D:
    return Coord2D(len(grid[0]), len(grid))


def dimensions_3d(grid: Grid3D[T]) -> Coord3D:
    return Coord3D(len(grid[0][0]), len(grid[0]), len(grid))


def boundaries_2d(grid: Grid2D[T]) -> Coord2D:
    return Coord2D(len(grid[0]) - 1, len(grid) - 1)


def boundaries_3d(grid: Grid3D[T]) -> Coord3D:
    return Coord3D(len(grid[0][0]) - 1, len(grid[0]) - 1, len(grid) - 1)


def set_element_2d(grid: MutableGrid2D[T], pos: _Coord2D, value: T) -> None:
    p = _c2d(pos)
    grid[p.y][p.x] = value


def get_element_2d(grid: Grid2D[T], pos: _Coord2D) -> T:
    p = _c2d(pos)
    return grid[p.y][p.x]


def set_element_3d(grid: MutableGrid3D[T], pos: _Coord3D, value: T) -> None:
    p = _c3d(pos)
    grid[p.z][p.y][p.x] = value


def get_element_3d(grid: Grid3D[T], pos: _Coord3D) -> T:
    p = _c3d(pos)
    return grid[p.z][p.y][p.x]


def iter_grid_2d(grid: Grid2D[T]) -> Iterator[tuple[Coord2D, T]]:
    for y, row in enumerate(grid):
        for x, value in enumerate(row):
            yield Coord2D(x, y), value


def iter_grid_3d(grid: Grid3D[T]) -> Iterator[tuple[Coord3D, T]]:
    for z, plane in enumerate(grid):
        for y, row in enumerate(plane):
            for x, value in enumerate(row):
                yield Coord3D(x, y, z), value


########## Simplify 2D interface ####################

Coord = Coord2D
Grid: TypeAlias = list[list[T]] | tuple[tuple[T, ...], ...]
MutableGrid: TypeAlias = list[list[T]]
manhattan = manhattan_2d
is_within = is_within_2d
neighbors = neighbors_2d
bounded_neighbors = bounded_neighbors_2d
neighbors_full = neighbors_full_2d
bounded_neighbors_full = bounded_neighbors_full_2d

create_grid = create_grid_2d
width = width_2d
height = height_2d
dimensions = dimensions_2d
boundaries = boundaries_2d
set_element = set_element_2d
get_element = get_element_2d
iter_grid = iter_grid_2d

########## private functions ####################


def _c2d(coord: _Coord2D) -> Coord2D:
    return coord if isinstance(coord, Coord2D) else Coord2D(*coord)


def _c3d(coord: _Coord3D) -> Coord3D:
    return coord if isinstance(coord, Coord3D) else Coord3D(*coord)


_neighbor_direct_2d: list[Coord2D] = []
_neighbor_corner_2d: list[Coord2D] = []
_neighbor_direct_3d: list[Coord3D] = []
_neighbor_edge_3d: list[Coord3D] = []
_neighbor_corner_3d: list[Coord3D] = []


def _initNeighbors() -> None:
    global _neighbor_direct_2d
    global _neighbor_corner_2d
    global _neighbor_direct_3d
    global _neighbor_edge_3d
    global _neighbor_corner_3d
    for x, y, z in itertools.product((-1, 0, 1), repeat=3):
        if (x, y, z) == (0, 0, 0):
            continue
        _neighbor_corner_3d.append(Coord3D(x, y, z))

        if x != 0 and y != 0 and z != 0:
            continue
        _neighbor_edge_3d.append(Coord3D(x, y, z))

        if z == 0:
            _neighbor_corner_2d.append(Coord2D(x, y))

        if (x ^ y ^ z) & 1 == 0:
            continue
        _neighbor_direct_3d.append(Coord3D(x, y, z))

        if z == 0:
            _neighbor_direct_2d.append(Coord2D(x, y))


_initNeighbors()
