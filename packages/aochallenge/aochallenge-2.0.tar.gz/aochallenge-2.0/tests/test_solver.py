import pathlib
import pytest
import sys

from aochallenge import Solver, Solution


# TEST SOLVER

def test_solver_parts(capsys):
    class MySolution(Solver):
        def part1(self):
            return 42
        def part2(self):
            return 69.96
        def part3(self):
            return "Hello World!"

    expected = "1: 42\n2: 69.96\n3: Hello World!\n"
    MySolution().main()
    captured = capsys.readouterr()
    assert captured.out == expected


def test_solver_more(capsys):
    class MySolution(Solver):
        def solve_more(self):
            yield 42
            yield 69.96
            yield "Hello World!"

    expected = "1: 42\n2: 69.96\n3: Hello World!\n"
    MySolution().main()
    captured = capsys.readouterr()
    assert captured.out == expected


# TEST (DEPRECATED) SOLUTION

@pytest.fixture
def solution():
    return Solution()


@pytest.fixture
def argv():
    oldargv = sys.argv
    testpath = pathlib.Path(__file__).parent.resolve()
    srcname = str(testpath) + "/aoc.py"
    sys.argv = [srcname]
    yield sys.argv
    sys.argv = oldargv


INPUTS = {
    None: "1,2,3,4\n",
    "col": "1\n2\n3\n4\n",
    "char": "123\n456\n",
    "int": "1 2 3\n4 5 6\n",
    "float": "1.2::2.3::3.4\n4.5::5.6::6.7\n",
    "mixed": "row1,45,6.9,3.4\nrow2,78,7.9,4.2\n",
    "inttype": 123456,
}

@pytest.mark.parametrize(
    "input, params, data",
    (
        ("", (), "1,2,3,4\n"),
        ("", (False, ","), ["1", "2", "3", "4"]),
        ("", (False, ",", int), [1, 2, 3, 4]),
        ("", (True, ",", int), [[1, 2, 3, 4]]),
        ("col", (True,), ["1", "2", "3", "4"]),
        ("col", (True, None, int), [1, 2, 3, 4]),
        ("int", (False,), "1 2 3\n4 5 6\n"),
        ("int", (True, " "), [["1", "2", "3"], ["4", "5", "6"]]),
        ("int", (True, " ", int), [[1, 2, 3], [4, 5, 6]]),
        ("int", (False, " "), ["1", "2", "3"]),
        ("int", (False, " ", int), [1, 2, 3]),
        ("char", (True, ""), [["1", "2", "3"], ["4", "5", "6"]]),
        ("char", (False, ""), ["1", "2", "3"]),
        ("char", (False, "", int), [1, 2, 3]),
        ("char", (True, "", int), [[1, 2, 3], [4, 5, 6]]),
        ("float", (True, "::", float), [[1.2, 2.3, 3.4], [4.5, 5.6, 6.7]]),
        (
            "mixed",
            (True, ",", (str, int, float)),
            [["row1", 45, 6.9, 3.4], ["row2", 78, 7.9, 4.2]],
        ),
        ("inttype", tuple(), 123456),
    ),
)
def test_load(input, params, data, argv, solution):
    if input:
        sys.argv.append(input)
    read_data = solution.load(*params, lut=INPUTS)
    assert read_data == data


def test_load_file(argv, solution):
    read_data = solution.load(True, ",", int)
    assert read_data == [[1, 2, 3], [4, 5, 6]]


def test_variant(argv, solution):
    assert solution.variant() is None
    sys.argv.append("-t")
    assert solution.variant() == "-t"


def test_parts(capsys):
    class MySolution(Solution):
        def part1(self):
            return 42

        def part2(self):
            return 69.96

        def part3(self):
            return "Hello World!"

    expected = "1: 42\n2: 69.96\n3: Hello World!\n"
    MySolution().main()
    captured = capsys.readouterr()
    assert captured.out == expected


def test_solve_more(capsys):
    class MySolution(Solution):
        def solve_more(self):
            yield 42
            yield 69.96
            yield "Hello World!"

    expected = "1: 42\n2: 69.96\n3: Hello World!\n"
    MySolution().main()
    captured = capsys.readouterr()
    assert captured.out == expected


@pytest.mark.parametrize(
    "data, printed",
    (
        ([[12, 34], [56, 78]], "1234\n5678\n"),
        (("##.", ".#.", ".##"), "##.\n.#.\n.##\n"),
    ),
)
def test_print_condensed(data, printed, capsys, solution):
    solution.print_condensed(data)
    captured = capsys.readouterr()
    assert captured.out == printed


@pytest.mark.parametrize(
    "data, printed", (([[1, 34], [True, "xyz"]], "1,34\nTrue,xyz\n"),)
)
def test_print_csv(data, printed, capsys, solution):
    solution.print_csv(data)
    captured = capsys.readouterr()
    assert captured.out == printed


@pytest.mark.parametrize(
    "data, printed", (([[1, 3456], [True, "xyz"]], "   1 3456\nTrue xyz \n"),)
)
def test_print_arranged(data, printed, capsys, solution):
    solution.print_arranged(data)
    captured = capsys.readouterr()
    assert captured.out == printed
