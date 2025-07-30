from typing import Any

from verse.content.image import Image, ImageParam
from verse.core import Component, Response, operation


class ImageCaptioning(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @operation()
    def caption(
        self,
        image: str | bytes | Image | ImageParam | dict,
        max_length: int | None = None,
        **kwargs: Any,
    ) -> Response[str]:
        """Generate caption for image.

        Args:
            image: Image.

        Returns:
            Caption.
        """
        ...

    @operation()
    def batch(
        self,
        images: list[str | bytes | Image | ImageParam | dict],
        max_length: int | None = None,
        **kwargs: Any,
    ) -> Response[list[str]]:
        """Generate captions for batch of images.

        Args:
            images: List of images.

        Returns:
            List of captions.
        """
        ...

    @operation()
    async def acaption(
        self,
        image: str | bytes | Image | ImageParam | dict,
        **kwargs: Any,
    ) -> Response[str]:
        """Generate caption for image.

        Args:
            image: Image.

        Returns:
            Caption.
        """
        ...

    @operation()
    async def abatch(
        self,
        images: list[str | bytes | Image | ImageParam | dict],
        **kwargs: Any,
    ) -> Response[list[str]]:
        """Generate captions for batch of images.

        Args:
            images: List of images.

        Returns:
            List of captions.
        """
        ...
