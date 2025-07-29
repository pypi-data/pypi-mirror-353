from verse.content.image import Image
from verse.core import DataModel


class ImageGenerationResult(DataModel):
    """
    The result of image generation operation.
    """

    images: list[Image]
