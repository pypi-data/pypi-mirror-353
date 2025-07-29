from typing import Any

from verse.content.image import Image, ImageParam
from verse.core import Component, Response, operation


class ZeroShotImageClassification(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @operation()
    def classify(
        self,
        image: str | bytes | Image | ImageParam | dict,
        classes: list[str],
        **kwargs: Any,
    ) -> Response[list[float]]:
        """Zero-shot classification of image with provided texts.

        Args:
            image: Image to classify.
            texts: List of classes as texts.

        Returns:
            Classification results.
        """
        ...

    @operation()
    def batch(
        self,
        images: list[str | bytes | Image | ImageParam | dict],
        classes: list[str],
        **kwargs: Any,
    ) -> Response[list[list[float]]]:
        """Zero-shot classification of images with provided texts.

        Args:
            images: Images to classify.
            texts: List of classes as texts.

        Returns:
            List of classification results.
        """
        ...

    @operation()
    async def aclassify(
        self,
        image: Image,
        classes: list[str],
        **kwargs: Any,
    ) -> Response[list[float]]:
        """Zero-shot classification of image with provided texts.

        Args:
            image: Image to classify.
            texts: List of classes as texts.

        Returns:
            Classification results.
        """
        ...

    @operation()
    async def abatch(
        self,
        images: list[Image],
        classes: list[str],
        **kwargs: Any,
    ) -> Response[list[list[float]]]:
        """Zero-shot classification of images with provided texts.

        Args:
            images: Images to classify.
            texts: List of classes as texts.

        Returns:
            List of classification results.
        """
        ...
