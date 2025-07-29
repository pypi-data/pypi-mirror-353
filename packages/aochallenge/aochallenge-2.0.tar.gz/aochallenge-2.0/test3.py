#!/usr/bin/python3 -u

from aochallenge import *


class Solution(Solver):

    def __init__(self) -> None:
        data = load(True,',',int)
#>        for r, row in enumerate(data):
#>            for c, content in enumerate(row):
        print_arranged(data)

#>    def part1(self) -> int:

#>    def part2(self) -> int:

#>    def solve_more(self) -> Generator[int, None, None]:

# print_condensed, print_csv, print_arranged


solution: Solution = Solution()
solution.main()
