import pytest
import os
from PIL import Image

from aochallenge import save_image

@pytest.mark.parametrize(
    "grid, lut, image",
    (
        (["#.",".#"], {".":0x2a890d, "#":0x123456}, [[0x123456,0x2a890d],[0x2a890d,0x123456]]),
        ([[1,2,1],[3,3,1]], {1:0x123456, 2:0x2a890d, 3:0xabcdef}, [[0x123456,0x2a890d,0x123456],[0xabcdef,0xabcdef,0x123456]]),
    )
)
def test_create_test_image(grid, lut, image, tmp_path):
    output_path = tmp_path / "test.png"

    save_image(output_path, grid, lut)

    assert output_path.exists()

    img = Image.open(output_path)
    width = len(image[0])
    height = len(image)
    assert img.size == (width, height)
    assert img.mode == "RGB"
    for y in range(height):
        for x in range(width):
            color = image[y][x]
            expected = (color >> 16, (color >> 8) & 0xff, color & 0xff)
            assert img.getpixel((x, y)) == expected
