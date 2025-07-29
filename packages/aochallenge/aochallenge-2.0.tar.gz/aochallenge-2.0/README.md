# AOChallenge Module

The  module   is  designed   to  speed  up   the  solution   of  certain
coding   challenges.   The   module    is   inspired   by   [Advent   of
Code](https://adventofcode.com/), I have not  used it for anything else,
but it is probably useful for other things.

The use  of the module is  different from the traditional  ones, my goal
was to  be able  to create  a new solution  easily. The  `Solution` base
class provided  by the  module contains some  frequently used  or useful
functions for debugging and only the solutions need to be added.

Each time I start from the code below.

```python
#!/usr/bin/python3 -u

from aochallenge import *


class Solution(Solver):

    def __init__(self):
        data = load(True,',',int)

#    def part1(self):

#    def part2(self):

#    def solve_more(self):

solution = Solution()
solution.main()
```

To be more precise, I also use  type annotation, which I have taken from
here.

The `part1`  and `part2` methods  are called  and the returned  value is
displayed by the original class. If the two parts of the challenge build
on each other,  you can also use `solve_more` (generator),  in which the
solutions are returned with the `yield` keyword, so that the computation
can  continue  without  saving  previous results.  Check  out  also  the
[example](#example) at the end of this document.

In the constructor, it makes sense to load and, if necessary, preprocess
the input data, which is well done  by the load function of the Solution
class. Note  that this function  examines the program's  input arguments
and decides which input file to load (test or main) based on them.

## Importing data

For  each challenge  there are  one  or more  test inputs  and there  is
your  challenge one.  The  class expects  the input  files  to be  named
appropriately to be able to  load automatically, but also arbitrary file
name can be  specified. Default filebname is 'input'  or 'input.txt' and
test  file  variant  can  be  appended to  'input',  i.e.  'input-t'  or
'input-t.txt'.

    aoc/2022/01/
    |---- aoc.py        source code
    |---- input-t.txt   test input
    \---- input.txt     challenge input

In this case, you can run your code with the test data as follows:

    $ ./aoc.py -t

And with the challenge data, simply:

    $ ./aoc.py

In some special cases  the input is a single line of  data or some other
simple constructs.  In this case it  is unnecessary to create  files for
each, you can simply pass a look-up-table to the `load` function. E.g.

```python
INPUT = {
    None: 'My challenge input data',
    't': 'My test 1 input data',
    't2': 'My test 2 input data',
}
...
def __init__(self):
    data = self.load(lut=INPUT)
    ...
```

If you need which variant the solution  has been run with, you can check
it with `variant`. It returns `None` if no variant has bee given and the
variant id (E.g. `'-t'`) if it has been:

```python
def __init__(self):
    ...
    if variant() is not None:
        # test variant
```

### Using `load` method

The `load`  method is used to  prepare the data for  further processing.
The input  can come from a  file or from a  predefined look-up-table. If
the latter is not specified, file handling is automatic (see above).

`load` function does  not only import data, but  does some preprocessing
on them:

```python
def load(self,
        splitlines: bool = False,
        splitrecords: str | None = None,
        recordtype:  list[type] | tuple[type, ...] | type | None = None,
        *,
        lut: dict[str | None, Any] | None = None,
        filename: str | None = None
        ) -> list[str | int | list]
```

Parameters:

- `splitlines`: boolean  value whether the  input data lines have  to be
  splitted into a list.
- `splitrecords`:  string value  used to  separate the  records in  each
  line. For example, if there  are comma-separated values, this field is
  ",". If set to `None`, items within the row are not split.
- `recordtype`: type of records. For example, if the values are numbers,
  it  can  be `int`  or  even  `float`.  The  `load` function  does  the
  conversion. If  the parameter type  is `list` or `tuple`,  the various
  fields may  have different types.  E.g. `(str, list)` means,  that the
  first record should be a `str`, but all further ones have to be casted
  to `int`.
- `lut` (keyword  only parameter): if  this parameter is  specified, the
  input data will be read from it instead of from an input file.
- `filename` (keyword only  parameter): input file's name.  Note, that a
  `@@` in in  the filename will be  replaced by the variant.  If file is
  not found, `load` tries to add a '.txt' extension and open that one.

Note, that  if `splitlines`  is `False`  but `splitrecords`  is defined,
only the  first row  will be processed.  This means that  if you  have a
one-row data set, the return element  is not a two-dimensional list with
a single nested list, but a simple list of values from the first row.

## Using grids

The  purpose  of the  grid  submodule  is  to  handle 2D/3D  arrays  and
coordinates. It provides types and  functions that are frequently useful
in Advent of Code  challenges. Here are a few examples of  how it can be
used:

```python
def blur(src: grid.Grid[int]) -> grid.Grid[int]:
    dst = grid.create_grid(src, 0)
    for coord, px in grid.iter_grid(src):
        neighbors = grid.bounded_neighbors_full(coord, (0, 0), grid.boundaries(src))
        for ncoord in neighbors:
            px += grid.get_element(src, ncoord)
        pxcnt = len(neighbors) + 1
        grid.set_element(dst, coord, px // 9)
    return dst
```

```python
area: Grid2D[int] = [[]]
...
colsums = [0] * grid.width(area)
rowsums = [0] * grid.height(area)
for (x, y), v in grid.iter_grid(area):
    colsums[x] += v
    rowsums[y] += v
```

### Types

- `Coord2D` (or  `Coord`), `Coord3D`: A 2D/3D  coordinate represented as
  a  hashable  named  tuple  with  x, y  (and  z)  components.  Supports
  vector-style addition and subtraction.
- `Grid2D` (or `Grid`),`Grid3D`: Type alias for a 2D/3D grid of elements
  of type T, represented as a sequence of sequences (e.g., list or tuple
  of list/tuple).
- `MutableGrid2D`  (or `MutableGrid`),`MutableGrid3D`: Type alias  for a
  mutable 2D/3D grid of type T, specifically a list of lists.

### Functions

The  functions below  can also  be used  with `_2d`  and `_3d`  suffixes
(e.g., `neighbors_2d` and `neighbors_3d`),  depending on your needs. The
3D variants correspond to the  `Coord3D` and `Grid3D[T]` types. Omitting
the  suffix defaults  to 2D  usage. Note  that some  functions are  only
available in a 3D context. This is clearly indicated where applicable.

Coordinate operations:

- `manhattan(a: Coord, b: Coord) -> int`: Returns the Manhattan distance
  between two 2D/3D coordinates.
- `is_within(p: Coord, corner1: Coord, corner2: Coord) -> bool`: Returns
  True  if the  2D/3D  coordinate `p`  lies within  or  on the  boundary
  defined by the two opposite  dcorners. Assumes corner1 has the smaller
  coordinate values in all dimensions.
- `neighbors(coord: Coord)  -> list[Coord]`: Returns the  list of direct
  (side-adjacent) neighbors of the given 2D/3D coordinate.
- `bounded_neighbors(coord:  Coord, corner1:  Coord, corner2:  Coord) ->
  list[Coord]`: Returns the list  of direct (side-adjacent) neighbors of
  the 2D/3D  coordinate `coord`  that lie within  the bounds  defined by
  `corner1` and `corner2`  Assumes. `corner1` has the  smaller values in
  all dimensions .
- `neighbors_full(coord: Coord) -> list[Coord]`: Returns the list of all
  neighbors of the  given 2D/3D coordinate, including  those adjacent by
  faces, edges, and corners (8/26-directional neighbors).
- `bounded_neighbors_full(coord: Coord, corner1:  Coord, corner2: Coord)
  -> list[Coord]`: Returns the list of  all neighbors of the given 2D/3D
  coordinate,  including those  adjacent  by faces,  edges, and  corners
  (8/26-directional  neighbors) that  lie within  the bounds  defined by
  `corner1` and `corner2`  Assumes. `corner1` has the  smaller values in
  all dimensions .
- `neighbors_edge_3d(coord: Coord3D) -> list[Coord3D]`: Returns the list
  of 3D neighbors  adjacent to the given coordinate by  faces and edges,
  excluding corner-adjacent neighbors.
- `bounded_neighbors_edge_3d(coord:  Coord3D,  corner1: Coord,  corner2:
  Coord) -> list[Coord3D]`: Returns the list of 3D neighbors adjacent by
  faces and  edges that lie within  the bounds defined by  `corner1` and
  `corner2`,  excluding  corner  neighbors. Assumes  `corner1`  has  the
  smaller coordinate values in all dimensions.

Grid operations:

- `create_grid_2d`,  `create_grid_3d`: Returns with a  2D/3D grid filled
  up with th default value.
- `width_2d`,  `height_2d`, `width_3d`, `height_3d`,  `depth_3d`: Return
  the corresponding dimension value of the given 2D/3D grid
- `dimension_2d`, `dimension_3d`:  Return  the  dimensions of  the given
  2D/3D grid in `Coord2D`/`Coord3D` format
- `boundaries_2d`, `boundaries_3d`: Return the  boundariess of the given
  2D/3D grid  in `Coord2D`/`Coord3D` format.  Note that it  differs from
  dimensions in that it includes the  last index - meaning each value is
  one less than it would be in that case.
- `set_element_2d`,  `set_element_3d`: Sets  the  element  at the  given
  2D/3D coordinate in the mutable  grid to the specified value (modifies
  the grid in place).
- `get_element_2d`, `get_element_3d`:  Returns the element at  the given
  2D/3D coordinate in the grid.
- `iter_grid_2d`,  `iter_grid_3d`:  Iterator,   yields  pairs  of  2D/3D
  coordinates  and  their corresponding  values  by  iterating over  all
  elements in the 2D/3D grid.

## Displaying temporary results

The  class  contains  some  debugging  solutions  to  display  temporary
results.

- `print_condensed(grid: Grid2D[T])`:  Prints content  of  a  2D grid  of
  characters "condensed". E.g. if data is

      [['#', '#', '.'], ['.', '#', '.'], ['.', '#', '#']]`

  the following will be printed:

      ##.
      .#.
      .##

  Note that the 2D grid can be also a list of strings.
- `def  print_csv(grid: Grid2D[T])`:  Prints content of  a 2-dimensional
  container in a comma separated way
-   `def  print_arranged(grid:   Grid2D[T])`:   Prints   content  of   a
  2-dimensional container arranged into columns
-  `def  print_solution(solution:  Solver)`:   Prints  properties  of  a
  `Solver` based object

## Data visualization

Sometimes  it's necessary  to  save an  image -  either  to analyze  the
current  state  or simply  to  visualize  the result.  The  `save_image`
function provides this capability.

```python
scene Grid2D[str] = [
    ["#", "#", "#", "#", "#"], 
    ["#", "S", ".", ".", "#"], 
    ["#", ".", "#", ".", "#"], 
    ["#", ".", "#", "E", "#"], 
    ["#", "#", "#", "#", "#"], 
]
colors : ColorLUT[str] = {
    ".": 0xdddddd, # light gray
    "#": 0x000900, # black
    "S": 0xff0900, # red
    "E": 0x0009ff, # blue
}
save_image("scene.png", scene, colors)
```

Festures:

- `ColorLUT[T]`:  a dictionary-based look-up  table that maps  values of
  type T to RGB color integers in 0xRRGGBB format.
- `save_image(filename:  str,  grid: Grid2D[T],  colors:  ColorLUT[T])`:
  converts grid to  an image using the  color table and saves  it to the
  specified file path.


## Autoimported modules and functions

The **aochallenge**  module also imports several  commonly used standard
functions and modules when used with `from aochallenge import *`.

Imported modules:

- `sys`
- `re`

Imported functions:

- `cache` (from `functools`)
- `lru_cache` (from `functools`)
- `combinations` (from `itertools`)
- `count` (from `itertools`)
- `product` (from `itertools`)
- `Generator` (from `collections.abc`)
- `dataclass` (from `dataclasses`)
- `field` (from `dataclasses`)
- `copy` (from `copy`)
- `deepcopy` (from `copy`)
- `Callable` (from `typing`)
- `cast` (from `typing`)
- `NamedTuple` (from `typing`)

## Example

**PART 1**: Add up  all the numbers in each row  separated by commas and
print the maximum of these sums.

**PART 2**: Find the 3 largest sums, add them up and determine the final
result.

Using `part1` and `part2`:

```python
#!/usr/bin/python2 -u

from aochallenge import *

class Solution(Solver):
    def __init__(self):
        self.data = load(True,',',int)

    def part1(self):
        return max(sum(row) for row in self.data)

    def part2(self):
        return sum(sorted(sum(row) for row in self.data)[-4:])

solution = Solution()
solution.main()
```

Using `solve_more`:

```python
#!/usr/bin/python2 -u

from aochallenge import *

class Solution(Solver):
    def __init__(self):
        self.data = load(True,',',int)

    def solve_more(self):
        sums = sorted(sum(row) for row in self.data)
        yield sums[-2]
        yield sum(sums[-4:])

solution = Solution()
solution.main()
```
