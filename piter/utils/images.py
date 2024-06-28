import numpy as np
from PIL import Image
import io
import base64


def numpy_to_jpeg_base64_url(numpy_img, quality=70):
    # Convert the NumPy array to a PIL image
    pil_img = Image.fromarray(np.uint8(numpy_img))

    # Save the PIL image as a JPEG file in memory with the specified quality
    buffer = io.BytesIO()
    pil_img.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)

    # Encode the JPEG file in Base64
    base64_encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Create a data URL from the Base64 encoded string
    data_url = f"data:image/jpeg;base64,{base64_encoded}"

    return data_url
