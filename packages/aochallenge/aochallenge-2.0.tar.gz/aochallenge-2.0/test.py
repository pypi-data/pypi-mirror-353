#!/usr/bin/python3 -u

import aochallenge as aoc
from aochallenge.grid import *
#>from aochallenge import save_image
#>import copy
#>from collections.abc import Generator
#>from functools import cache
#>from itertools import combinations, product


class Solution(aoc.Solution):

    def __init__(self) -> None:
        super().__init__()
        data = self.load(True,'')
        for r, row in enumerate(data):
            for c, content in enumerate(row):
                pass
#>        self.map = data
#>        self.height = len(self.map)
#>        self.width = len(self.map[0])
#>        self.s = "abc"
#>        self.x = 42
#>        self.y = 13.7
#>        self.arr = [1,2,3]
#>        print(self.__dict__)
#>        print("Content")
#>        aoc.print_solution(self, indent="  ")
#>        print(aoc.neighbours2D(aoc.Coord2D(5,7)))
#>        print(self.__dict__)

#>        print(neighbours_2d((5,7)))
#>        print(bounded_neighbours_2d((5,7),(5,3),(8,7)))
#>        map = [list(s) for s in ("abc","efg","hij")]
#>        aoc.print_condensed(map)
#>#>        print(get_element_2d(map,(1,1))) 
#>        map = [list(s) for s in (".#.","###",".#.")]
#>        lut = {".":0xffffff, "#":0xff0000}
#>        aoc.save_image("my.png",map,lut)
        map = (".#.","###",".#.")
        aoc.print_condensed(map)
        lut = {".":0xffffff, "#":0xff0000}
        aoc.save_image("my.png",map,lut)
        print(get_element(map, (1,1)))
        set_element(map, (1,1), '$')
        set_element(13, 13, '$')

#>
#>    def part1(self) -> int:

#>    def part2(self) -> int:

#>    def solve_more(self) -> Generator[int, None, None]:

# print_condensed, print_csv, print_arranged


solution: Solution = Solution()
solution.main()
