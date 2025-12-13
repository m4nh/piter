import numpy as np
from PIL import Image
import io
import base64
import typing as t
import colour
import pathlib as pl


def numpy_to_base64_url(
    numpy_img: np.ndarray,
    quality: int = 70,
    extension: str = "jpeg",
):
    # Convert the NumPy array to a PIL image
    pil_img = Image.fromarray(np.uint8(numpy_img))

    # Save the PIL image as a JPEG file in memory with the specified quality
    buffer = io.BytesIO()
    pil_img.save(buffer, format=extension, quality=quality)
    buffer.seek(0)

    # Encode the JPEG file in Base64
    base64_encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Create a data URL from the Base64 encoded string
    data_url = f"data:image/{extension};base64,{base64_encoded}"

    return data_url


def image_file_to_base64_url(image_path: t.Union[str, pl.Path], quality: int = 70):
    image_path = str(image_path)
    image = Image.open(image_path)
    extension = image_path.split(".")[-1]
    return numpy_to_base64_url(np.array(image), quality=quality, extension=extension)


MATERIAL_DESIGN_COLORS_LIST = [
    # red (500)
    (244, 67, 54),
    # green (500)
    (76, 175, 80),
    # blue (500)
    (33, 150, 243),
    # yellow (500)
    (255, 235, 59),
    # purple (500)
    (156, 39, 176),
    # teal (500)
    (0, 150, 136),
    # pink (500)
    (233, 30, 99),
    # orange (500)
    (255, 152, 0),
    # brown (500)
    (121, 85, 72),
    # grey (500)
    (158, 158, 158),
    # deep orange (500)
    (255, 87, 34),
    # cyan (500)
    (0, 188, 212),
    # lime (500)
    (205, 220, 57),
    # light blue (500)
    (3, 169, 244),
    # amber (500)
    (255, 193, 7),
]


def label_to_color(
    label: int, format: t.Literal["rgb", "rgba", "hex"] = "hex"
) -> t.Union[t.Tuple[int, int, int], t.Tuple[int, int, int, int], str]:
    rgb = MATERIAL_DESIGN_COLORS_LIST[label % len(MATERIAL_DESIGN_COLORS_LIST)]

    rgb = [float(x) / 255 for x in rgb]

    if format == "rgb":
        return rgb
    elif format == "rgba":
        return rgb + (255,)
    elif format == "hex":
        return colour.rgb2hex(rgb)


def color_rgb_to_hex(color: t.Union[t.Tuple[int, int, int], t.List[int]]) -> str:
    c = colour.Color()
    r = color[0] / 255
    g = color[1] / 255
    b = color[2] / 255
    c.set_rgb([r, g, b])
    return c.get_hex_l()
