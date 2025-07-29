#!/usr/bin/python3

#import os
import sys
from aochallenge import grid

def fail(text, *args, **kwargs):
    print("FAILED: "+text, *args, file=sys.stderr, **kwargs)
    sys.exit()

def blur(src: grid.Grid[int]) -> grid.Grid[int]:
    dst = grid.create_grid(src, 0)
    for coord, px in grid.iter_grid(src):
        neighbors = grid.bounded_neighbors_full(coord, (0, 0), grid.boundaries(src))
        for ncoord in neighbors:
            px += grid.get_element(src, ncoord)
        pxcnt = len(neighbors) + 1
        grid.set_element(dst, coord, px // 9)
    return dst

def main():
    area: Grid2D[int] = [[1,2,3],[4,5,6]]
    colsums = [0] * grid.width(area)
    rowsums = [0] * grid.height(area)
    for (x, y), v in grid.iter_grid(area):
        colsums[x] += v
        rowsums[y] += v
    print(colsums)
    print(rowsums)
    image: Grid2D[int] = [[100,0,0,0],[0,0,0,0],[0,0,100,0],[0,0,0,0]]
    blured = blur(image)
    print(blured)
    return 0

main()
