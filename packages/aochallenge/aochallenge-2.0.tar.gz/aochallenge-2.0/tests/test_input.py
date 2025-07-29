import os
import pathlib
import pytest
import sys

from aochallenge import load, variant


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
    "args, params, data",
    (
        ([], (), "1,2,3,4\n"),
        ([], (False, ","), ["1", "2", "3", "4"]),
        ([], (False, ",", int), [1, 2, 3, 4]),
        ([], (True, ",", int), [[1, 2, 3, 4]]),
        (["col"], (True,), ["1", "2", "3", "4"]),
        (["col"], (True, None, int), [1, 2, 3, 4]),
        (["int"], (False,), "1 2 3\n4 5 6\n"),
        (["int"], (True, " "), [["1", "2", "3"], ["4", "5", "6"]]),
        (["int"], (True, " ", int), [[1, 2, 3], [4, 5, 6]]),
        (["int"], (False, " "), ["1", "2", "3"]),
        (["int"], (False, " ", int), [1, 2, 3]),
        (["char"], (True, ""), [["1", "2", "3"], ["4", "5", "6"]]),
        (["char"], (False, ""), ["1", "2", "3"]),
        (["char"], (False, "", int), [1, 2, 3]),
        (["char"], (True, "", int), [[1, 2, 3], [4, 5, 6]]),
        (["float"], (True, "::", float), [[1.2, 2.3, 3.4], [4.5, 5.6, 6.7]]),
        (
            ["mixed"],
            (True, ",", (str, int, float)),
            [["row1", 45, 6.9, 3.4], ["row2", 78, 7.9, 4.2]],
        ),
        (["inttype"], tuple(), 123456),
    ),
)
def test_load(args, params, data, argv):
    sys.argv.extend(args)
    read_data = load(*params, lut=INPUTS)
    assert read_data == data


@pytest.mark.parametrize(
    "args, expected",
    (
        ([], [[11, 12, 13], [14, 15, 16]]),
        (["-t"], [[21, 22, 23], [24, 25, 26]]),
    ),
)
def test_load_default(args, expected, argv):
    sys.argv.extend(args)
    read_data = load(True, ",", int)
    assert read_data == expected


@pytest.mark.parametrize(
    "args, expected",
    (
        ([], [[11, 12, 13], [14, 15, 16]]),
        (["-t"], [[21, 22, 23], [24, 25, 26]]),
    ),
)
def test_load_filename(args, expected, argv):
    sys.argv.extend(args)
    filename = os.path.dirname(sys.argv[0]) + "/input@@.txt"
    read_data = load(True, ",", int, filename=filename)
    assert read_data == expected


def test_load_file_not_found(argv):
    filename = "nonexistent_file.txt"
    with pytest.raises(FileNotFoundError):
        load(True, ",", int, filename=filename)


@pytest.mark.parametrize(
    "args, expected",
    (
        ([], None),
        (["-t"], "-t"),
        (["--test"], "--test"),
    ),
)
def test_variant(args, expected, argv):
    sys.argv.extend(args)
    assert variant() == expected
