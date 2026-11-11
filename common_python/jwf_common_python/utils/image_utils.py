import io

try:
    from PIL import Image, ImageDraw
except ImportError as exc:
    raise ImportError(
        "Couldn't import pil. pip install --upgrade tencentcloud"
    ) from exc


def create_image(width: int, height: int, color: tuple[int, int, int]) -> bytes:
    # TODO 导入检测
    image = Image.new("RGB", (width, height), color)
    # create a memory buffer to store image
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_data = buffer.getvalue()
    return image_data
