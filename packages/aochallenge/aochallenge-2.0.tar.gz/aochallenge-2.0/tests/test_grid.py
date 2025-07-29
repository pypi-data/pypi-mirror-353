import pytest

from aochallenge.grid import *

########## Coord2D ####################

@pytest.mark.parametrize(
    "a, b, expected, should_fail",
    [
        (Coord2D(2, 3), Coord2D(1, -1), Coord2D(3, 2), False),
        (Coord2D(2, 3), (4, 5), Coord2D(6, 8), False),
        (Coord2D(2, 3), 10, Coord2D(12, 13), False),
        (Coord2D(2, 3), "invalid", None, True),
        (Coord2D(2, 3), [1, 2], None, True),
        (Coord2D(2, 3), None, None, True),
    ]
)
def test_add_2d(a, b, expected, should_fail):
    if should_fail:
        with pytest.raises(TypeError):
            _ = a + b
    else:
        assert a + b == expected


@pytest.mark.parametrize(
    "a, b, expected, should_fail",
    [
        (Coord2D(5, 7), Coord2D(2, 3), Coord2D(3, 4), False),
        (Coord2D(5, 7), (1, 2), Coord2D(4, 5), False),
        (Coord2D(5, 7), 3, Coord2D(2, 4), False),
        (Coord2D(5, 7), "wrong", None, True),
        (Coord2D(5, 7), [1, 2], None, True),
        (Coord2D(5, 7), {}, None, True),
    ]
)
def test_sub_2d(a, b, expected, should_fail):
    if should_fail:
        with pytest.raises(TypeError):
            _ = a - b
    else:
        assert a - b == expected

########## Coord3D ####################

@pytest.mark.parametrize(
    "a, b, expected, should_fail",
    [
        (Coord3D(1, 2, 3), Coord3D(4, 5, 6), Coord3D(5, 7, 9), False),
        (Coord3D(1, 2, 3), (4, 5, 6), Coord3D(5, 7, 9), False),
        (Coord3D(1, 2, 3), 10, Coord3D(11, 12, 13), False),
        (Coord3D(1, 2, 3), "invalid", None, True),
        (Coord3D(1, 2, 3), (1, 2), None, True),
        (Coord3D(1, 2, 3), None, None, True),
    ]
)
def test_add_3d(a, b, expected, should_fail):
    if should_fail:
        with pytest.raises(TypeError):
            _ = a + b
    else:
        assert a + b == expected

@pytest.mark.parametrize(
    "a, b, expected, should_fail",
    [
        (Coord3D(10, 10, 10), Coord3D(3, 4, 5), Coord3D(7, 6, 5), False),
        (Coord3D(10, 10, 10), (1, 2, 3), Coord3D(9, 8, 7), False),
        (Coord3D(10, 10, 10), 5, Coord3D(5, 5, 5), False),
        (Coord3D(10, 10, 10), [1, 2, 3], None, True),
        (Coord3D(10, 10, 10), (1, 2), None, True),
        (Coord3D(10, 10, 10), {}, None, True),
    ]
)
def test_sub_3d(a, b, expected, should_fail):
    if should_fail:
        with pytest.raises(TypeError):
            _ = a - b
    else:
        assert a - b == expected

########## distance ####################

@pytest.mark.parametrize(
    "a,b,expected",
    [
        (Coord2D(0, 0), Coord2D(0, 0), 0),
        (Coord2D(1, 2), Coord2D(4, 6), 7),
        (Coord2D(-1, -2), Coord2D(3, 1), 7),
        (Coord2D(5, 5), Coord2D(2, 1), 7),
    ]
)
def test_manhattan_2d(a, b, expected):
    assert manhattan_2d(a, b) == expected

@pytest.mark.parametrize(
    "a,b,expected",
    [
        (Coord3D(0, 0, 0), Coord3D(0, 0, 0), 0),
        (Coord3D(1, 2, 3), Coord3D(4, 6, 9), 13),
        (Coord3D(-1, -2, -3), Coord3D(3, 1, 2), 12),
        (Coord3D(5, 5, 5), Coord3D(2, 1, 0), 12),
    ]
)
def test_manhattan_3d(a, b, expected):
    assert manhattan_3d(a, b) == expected

########## is_within ####################

@pytest.mark.parametrize(
    "coord, corner1, corner2, expected",
    [
        (Coord2D(5, 5), Coord2D(0, 0), Coord2D(10, 10), True),
        ((5, 5), (0, 0), (10, 10), True),
        ((0, 0), (0, 0), (0, 0), True),
        ((-1, -1), (0, 0), (10, 10), False),
        ((11, 11), (0, 0), (10, 10), False),
        ((5, 11), (0, 0), (10, 10), False),
    ]
)
def test_is_within_2d(coord, corner1, corner2, expected):
    assert is_within_2d(coord, corner1, corner2) == expected


@pytest.mark.parametrize(
    "coord, corner1, corner2, expected",
    [
        (Coord3D(5, 5, 5), Coord3D(0, 0, 0), Coord3D(10, 10, 10), True),
        ((5, 5, 5), (0, 0, 0), (10, 10, 10), True),
        ((0, 0, 0), (0, 0, 0), (0, 0, 0), True),
        ((-1, -1, -1), (0, 0, 0), (10, 10, 10), False),
        ((5, 5, 11), (0, 0, 0), (10, 10, 10), False),
    ]
)
def test_is_within_3d(coord, corner1, corner2, expected):
    assert is_within_3d(coord, corner1, corner2) == expected

########## neighbors 2D ####################

@pytest.mark.parametrize(
    "coord, expected",
    [
        (Coord2D(0, 0), [Coord2D(0, 1), Coord2D(1, 0), Coord2D(0, -1), Coord2D(-1, 0)]),
        (Coord2D(2, 2), [Coord2D(2, 3), Coord2D(3, 2), Coord2D(2, 1), Coord2D(1, 2)]),
    ]
)
def test_neighbors_2d(coord, expected):
    assert sorted(neighbors_2d(coord)) == sorted(expected)


@pytest.mark.parametrize(
    "coord, corner1, corner2, expected",
    [
        (Coord2D(0, 0), Coord2D(0, 0), Coord2D(1, 1), [Coord2D(1, 0), Coord2D(0, 1)]),
        (Coord2D(1, 1), Coord2D(0, 0), Coord2D(1, 1), [Coord2D(0, 1), Coord2D(1, 0)]),
        (Coord2D(0, 0), Coord2D(5, 5), Coord2D(10, 10), []),
    ]
)
def test_bounded_neighbors_2d(coord, corner1, corner2, expected):
    assert sorted(bounded_neighbors_2d(coord, corner1, corner2)) == sorted(expected)


@pytest.mark.parametrize(
    "coord, expected",
    [
        (Coord2D(0, 0), [
            Coord2D(-1, -1), Coord2D(0, -1), Coord2D(1, -1),
            Coord2D(-1, 0),                  Coord2D(1, 0),
            Coord2D(-1, 1),  Coord2D(0, 1),  Coord2D(1, 1),
        ]),
        (Coord2D(1, 1), [
            Coord2D(0, 0), Coord2D(1, 0), Coord2D(2, 0),
            Coord2D(0, 1),                Coord2D(2, 1),
            Coord2D(0, 2), Coord2D(1, 2), Coord2D(2, 2),
        ]),
    ]
)
def test_neighbors_full_2d(coord, expected):
    assert sorted(neighbors_full_2d(coord)) == sorted(expected)


@pytest.mark.parametrize(
    "coord, corner1, corner2, expected",
    [
        (Coord2D(0, 0), Coord2D(0, 0), Coord2D(0, 0), []),
        (Coord2D(0, 2), Coord2D(0, 0), Coord2D(2, 2), [
            Coord2D(0, 1), Coord2D(1, 1),
                           Coord2D(1, 2),
        ]),
        (Coord2D(1, 0), Coord2D(0, 0), Coord2D(2, 2), [
            Coord2D(0, 0),                Coord2D(2, 0),
            Coord2D(0, 1), Coord2D(1, 1), Coord2D(2, 1),
        ]),
        (Coord2D(1, 1), Coord2D(0, 0), Coord2D(2, 2), [
            Coord2D(0, 0), Coord2D(1, 0), Coord2D(2, 0),
            Coord2D(0, 1),                Coord2D(2, 1),
            Coord2D(0, 2), Coord2D(1, 2), Coord2D(2, 2),
        ]),
        (Coord2D(1, 1), Coord2D(5, 5), Coord2D(10, 10), []),
    ]
)
def test_bounded_neighbors_full_2d(coord, corner1, corner2, expected):
    assert sorted(bounded_neighbors_full_2d(coord, corner1, corner2)) == sorted(expected)

########## neighbors 3D 5####################

@pytest.mark.parametrize(
    "coord, expected",
    [
        (Coord3D(0, 0, 0), [
            Coord3D(1, 0, 0), Coord3D(-1, 0, 0),
            Coord3D(0, 1, 0), Coord3D(0, -1, 0),
            Coord3D(0, 0, 1), Coord3D(0, 0, -1),
        ]),
        (Coord3D(1, 1, 1), [
            Coord3D(2, 1, 1), Coord3D(0, 1, 1),
            Coord3D(1, 2, 1), Coord3D(1, 0, 1),
            Coord3D(1, 1, 2), Coord3D(1, 1, 0),
        ]),
    ]
)
def test_neighbors_3d(coord, expected):
    assert sorted(neighbors_3d(coord)) == sorted(expected)


@pytest.mark.parametrize(
    "coord, corner1, corner2, expected",
    [
        (Coord3D(0, 0, 0), Coord3D(-1, -1, -1), Coord3D(0, 0, 0), [
            Coord3D(-1, 0, 0), Coord3D(0, -1, 0), Coord3D(0, 0, -1),
        ]),
        (Coord3D(5, 5, 5), Coord3D(0, 0, 0), Coord3D(4, 4, 4), []),
    ]
)
def test_bounded_neighbors_3d(coord, corner1, corner2, expected):
    assert sorted(bounded_neighbors_3d(coord, corner1, corner2)) == sorted(expected)


@pytest.mark.parametrize(
    "coord, expected",
    [
        (Coord3D(0, 0, 0), [
            Coord3D(1, 0, 0), Coord3D(-1, 0, 0),
            Coord3D(0, 1, 0), Coord3D(0, -1, 0),
            Coord3D(0, 0, 1), Coord3D(0, 0, -1),

            Coord3D(0,1,1),   Coord3D(1,0,1),   Coord3D(1,1,0),
            Coord3D(0,1,-1),  Coord3D(1,0,-1),  Coord3D(1,-1,0),
            Coord3D(0,-1,1),  Coord3D(-1,0,1),  Coord3D(-1,1,0),
            Coord3D(0,-1,-1), Coord3D(-1,0,-1), Coord3D(-1,-1,0),
        ]),
    ]
)
def test_neighbors_edge_3d(coord, expected):
    assert sorted(neighbors_edge_3d(coord)) == sorted(expected)


@pytest.mark.parametrize(
    "coord, corner1, corner2, expected",
    [
        (Coord3D(0, 0, 0), Coord3D(0, 0, 0), Coord3D(0, 0, 0), []),
        (Coord3D(0, 0, 1), Coord3D(0, 0, 0), Coord3D(2, 2, 2), [
            Coord3D(1, 0, 1),
            Coord3D(0, 1, 1),
            Coord3D(0, 0, 2), Coord3D(0, 0, 0),

            Coord3D(0,1,2),  Coord3D(1,0,2),  Coord3D(1,1,1),
            Coord3D(0,1,0),  Coord3D(1,0,0),
        ]),
    ]
)
def test_bounded_neighbors_edge_3d(coord, corner1, corner2, expected):
    assert sorted(bounded_neighbors_edge_3d(coord, corner1, corner2)) == sorted(expected)


@pytest.mark.parametrize(
    "coord, expected_count",
    [
        (Coord3D(0, 0, 0), 26),
        (Coord3D(5, 5, 5), 26),
    ]
)
def test_neighbors_full_3d(coord, expected_count):
    result = neighbors_full_3d(coord)
    assert len(result) == expected_count
    assert Coord3D(0, 0, 0) not in result


@pytest.mark.parametrize(
    "coord, corner1, corner2, expected",
    [
        (Coord3D(0, 0, 0), Coord3D(0, 0, 0), Coord3D(0, 0, 0), []),
        (Coord3D(1, 1, 1), Coord3D(0, 0, 0), Coord3D(2, 2, 2), [
            Coord3D(0, 0, 0), Coord3D(0, 0, 1), Coord3D(0, 0, 2),
            Coord3D(0, 1, 0), Coord3D(0, 1, 1), Coord3D(0, 1, 2),
            Coord3D(0, 2, 0), Coord3D(0, 2, 1), Coord3D(0, 2, 2),
            Coord3D(1, 0, 0), Coord3D(1, 0, 1), Coord3D(1, 0, 2),
            Coord3D(1, 1, 0),                 Coord3D(1, 1, 2),
            Coord3D(1, 2, 0), Coord3D(1, 2, 1), Coord3D(1, 2, 2),
            Coord3D(2, 0, 0), Coord3D(2, 0, 1), Coord3D(2, 0, 2),
            Coord3D(2, 1, 0), Coord3D(2, 1, 1), Coord3D(2, 1, 2),
            Coord3D(2, 2, 0), Coord3D(2, 2, 1), Coord3D(2, 2, 2),
        ]),
    ]
)
def test_bounded_neighbors_full_3d(coord, corner1, corner2, expected):
    assert sorted(bounded_neighbors_full_3d(coord, corner1, corner2)) == sorted(expected)

########## Grid setters and getters 5####################

@pytest.mark.parametrize(
    "size, default, expected",
    [
        (Coord2D(2, 3), 0, [[0, 0], [0, 0], [0, 0]]),
        ([[1, 2], [3, 4]], ".", [[".", "."], [".", "."]]),
        (Coord2D(1, 1), "x", [["x"]]),
    ]
)
def test_create_grid_2d(size, default, expected):
    assert create_grid_2d(size, default) == expected

@pytest.mark.parametrize(
    "size, default, expected",
    [
        (Coord3D(2, 2, 1), 0, [[[0, 0], [0, 0]]]),  # 1 x 2 x 2
        ([[[1, 2], [3, 4]]], ".", [[[".", "."], [".", "."]]]),  # 1 x 2 x 2
        (Coord3D(1, 1, 1), "*", [[["*"]]]),
        (Coord3D(2, 1, 2), "-", [[["-", "-"]], [["-", "-"]]]),  # 2 x 1 x 2
    ]
)
def test_create_grid_3d(size, default, expected):
    assert create_grid_3d(size, default) == expected


@pytest.mark.parametrize(
    "grid, expected",
    [
        ([[1, 2], [3, 4]], 2),
        ([[0]], 1),
        ([[1, 2, 3], [4, 5, 6]], 3),
    ]
)
def test_width_2d(grid, expected):
    assert width_2d(grid) == expected

@pytest.mark.parametrize(
    "grid, expected",
    [
        ([[1, 2], [3, 4]], 2),
        ([[0]], 1),
        ([[1, 2, 3], [4, 5, 6]], 2),
    ]
)
def test_height_2d(grid, expected):
    assert height_2d(grid) == expected

@pytest.mark.parametrize(
    "grid, expected",
    [
        ([[[1, 2], [3, 4]]], 2),  # 1 x 2 x 2
        ([[[0]]], 1),             # 1 x 1 x 1
        ([[[1, 2, 3], [4, 5, 6]]], 3),  # 1 x 2 x 3
        ([[[1], [2]], [[3], [4]]], 1),  # 2 x 2 x 1
    ]
)
def test_width_3d(grid, expected):
    assert width_3d(grid) == expected

@pytest.mark.parametrize(
    "grid, expected",
    [
        ([[[1, 2], [3, 4]]], 2),  # 1 x 2 x 2
        ([[[0]]], 1),
        ([[[1, 2, 3], [4, 5, 6]]], 2),
        ([[[1], [2]], [[3], [4]]], 2),
    ]
)
def test_height_3d(grid, expected):
    assert height_3d(grid) == expected

@pytest.mark.parametrize(
    "grid, expected",
    [
        ([[[1, 2], [3, 4]]], 1),  # 1 x 2 x 2
        ([[[0]]], 1),
        ([[[1, 2, 3], [4, 5, 6]]], 1),
        ([[[1], [2]], [[3], [4]]], 2),  # 2 x 2 x 1
    ]
)
def test_depth_3d(grid, expected):
    assert depth_3d(grid) == expected


@pytest.mark.parametrize(
    "grid, expected",
    [
        ([[1, 2], [3, 4]], Coord2D(2, 2)),
        ([[0]], Coord2D(1, 1)),
        ([[1, 2, 3], [4, 5, 6]], Coord2D(3, 2)),
    ]
)
def test_dimensions_2d(grid, expected):
    assert dimensions_2d(grid) == expected


@pytest.mark.parametrize(
    "grid, expected",
    [
        ([[[1]]], Coord3D(1, 1, 1)),
        ([[[1, 2], [3, 4]]], Coord3D(2, 2, 1)),  # 1 x 2 x 2
        ([[[1], [2]], [[3], [4]]], Coord3D(1, 2, 2)),  # 2 x 2 x 1
    ]
)
def test_dimensions_3d(grid, expected):
    assert dimensions_3d(grid) == expected

@pytest.mark.parametrize(
    "grid, expected",
    [
        ([[1, 2], [3, 4]], Coord2D(1, 1)),
        ([[0]], Coord2D(0, 0)),
        ([[1, 2, 3], [4, 5, 6]], Coord2D(2, 1)),
    ]
)
def test_boundaries_2d(grid, expected):
    assert boundaries_2d(grid) == expected

@pytest.mark.parametrize(
    "grid, expected",
    [
        ([[[1]]], Coord3D(0, 0, 0)),
        ([[[1, 2], [3, 4]]], Coord3D(1, 1, 0)),
        ([[[1], [2]], [[3], [4]]], Coord3D(0, 1, 1)),
    ]
)
def test_boundaries_3d(grid, expected):
    assert boundaries_3d(grid) == expected


@pytest.mark.parametrize(
    "grid, pos, value, expected",
    [
        ([[0, 0], [0, 0]], Coord2D(0, 0), 1, [[1, 0], [0, 0]]),
        ([[9, 9], [9, 9]], Coord2D(1, 1), 5, [[9, 9], [9, 5]]),
    ]
)
def test_set_element_2d(grid, pos, value, expected):
    set_element_2d(grid, pos, value)
    assert grid == expected


@pytest.mark.parametrize(
    "grid, pos, expected",
    [
        ([[1, 2], [3, 4]], Coord2D(0, 0), 1),
        ([[1, 2], [3, 4]], Coord2D(1, 1), 4),
    ]
)
def test_get_element_2d(grid, pos, expected):
    assert get_element_2d(grid, pos) == expected


@pytest.mark.parametrize(
    "grid, pos, value, expected",
    [
        ([[[0, 0], [0, 0]], [[0, 0], [0, 0]]], Coord3D(0, 0, 0), 7,
         [[[7, 0], [0, 0]], [[0, 0], [0, 0]]]),
        ([[[1, 1], [1, 1]], [[1, 1], [1, 1]]], Coord3D(1, 1, 1), 9,
         [[[1, 1], [1, 1]], [[1, 1], [1, 9]]]),
    ]
)
def test_set_element_3d(grid, pos, value, expected):
    set_element_3d(grid, pos, value)
    assert grid == expected


@pytest.mark.parametrize(
    "grid, pos, expected",
    [
        ([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], Coord3D(0, 0, 0), 1),
        ([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], Coord3D(1, 1, 1), 8),
    ]
)
def test_get_element_3d(grid, pos, expected):
    assert get_element_3d(grid, pos) == expected

########## iterators ####################

@pytest.mark.parametrize(
    "grid, expected",
    [
        (
            [[1, 2], [3, 4]],
            [
                (Coord2D(0, 0), 1), (Coord2D(1, 0), 2),
                (Coord2D(0, 1), 3), (Coord2D(1, 1), 4)
            ]
        ),
        (
            [[5]],
            [(Coord2D(0, 0), 5)]
        ),
        (
            [],
            []
        ),
        (
            [[], []],
            []
        ),
    ]
)
def test_iter_grid_2d(grid, expected):
    result = list(iter_grid_2d(grid))
    assert result == expected

@pytest.mark.parametrize(
    "grid, expected",
    [
        (
            [[[1, 2], [3, 4]],[[5, 6], [7, 8]]],
            [
                (Coord3D(0, 0, 0), 1), (Coord3D(1, 0, 0), 2),
                (Coord3D(0, 1, 0), 3), (Coord3D(1, 1, 0), 4),
                (Coord3D(0, 0, 1), 5), (Coord3D(1, 0, 1), 6),
                (Coord3D(0, 1, 1), 7), (Coord3D(1, 1, 1), 8),
            ]
        ),
        (
            [[[5]]],
            [(Coord3D(0, 0, 0), 5)]
        ),
        (
            [],
            []
        ),
        (
            [[], []],
            []
        ),
    ]
)
def test_iter_grid_3d(grid, expected):
    result = list(iter_grid_3d(grid))
    assert result == expected
