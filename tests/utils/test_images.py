import base64
import io

import numpy as np
import pytest
from PIL import Image

from piter.utils import images


def _decode_data_url_to_array(data_url: str) -> np.ndarray:
    prefix, encoded = data_url.split(",", 1)
    decoded = base64.b64decode(encoded)
    with Image.open(io.BytesIO(decoded)) as img:
        return np.array(img)


def test_numpy_to_base64_url_round_trip_png():
    array = np.array(
        [[[10, 20, 30], [40, 50, 60]], [[70, 80, 90], [100, 110, 120]]],
        dtype=np.uint8,
    )

    data_url = images.numpy_to_base64_url(array, extension="png")

    assert data_url.startswith("data:image/png;base64,")
    restored = _decode_data_url_to_array(data_url)
    assert restored.dtype == np.uint8
    assert restored.shape == array.shape
    assert np.array_equal(restored, array)


def test_image_file_to_base64_url_uses_file_extension(tmp_path):
    array = np.array([[[255, 0, 0], [0, 255, 0]]], dtype=np.uint8)
    image_path = tmp_path / "sample.png"
    Image.fromarray(array).save(image_path)

    data_url = images.image_file_to_base64_url(image_path)

    assert data_url.startswith("data:image/png;base64,")
    restored = _decode_data_url_to_array(data_url)
    assert np.array_equal(restored, array)


def test_label_to_color_hex_matches_red():
    assert images.label_to_color(0, format="hex") == "#f44336"


def test_label_to_color_wraps_palette():
    assert images.label_to_color(0, format="hex") == images.label_to_color(
        15, format="hex"
    )


def test_label_to_color_rgb_values():
    expected = [33 / 255, 150 / 255, 243 / 255]
    assert images.label_to_color(2, format="rgb") == pytest.approx(expected)


def test_label_to_color_rgba_raises_type_error():
    with pytest.raises(TypeError):
        images.label_to_color(1, format="rgba")


def test_color_rgb_to_hex():
    assert images.color_rgb_to_hex((255, 0, 0)) == "#ff0000"
