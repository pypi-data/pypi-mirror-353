from typing import Any

from verse.content.image import Image, ImageParam
from verse.core import Component, Response, operation


class ImageEmbedding(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @operation()
    def embed(
        self,
        image: str | bytes | Image | ImageParam | dict,
        **kwargs: Any,
    ) -> Response[list[float]]:
        """Create embedding for image.

        Args:
            image: Image.

        Returns:
            Image embedding.
        """
        ...

    @operation()
    def compare(
        self,
        embedding1: list[float],
        embedding2: list[float],
        **kwargs,
    ) -> Response[float]:
        """Compare embeddings using cosine similarity.

        Args:
            embedding1: Embedding 1.
            embedding2: Embedding 2.

        Returns:
            Similarity score.
        """
        ...

    @operation()
    def batch(
        self,
        images: list[str | bytes | Image | ImageParam | dict],
        **kwargs: Any,
    ) -> Response[list[list[float]]]:
        """Create embedding for batch of images.

        Args:
            images: List of images.

        Returns:
            List of image embeddings.
        """
        ...

    @operation()
    def embed_text(
        self,
        text: str,
        **kwargs: Any,
    ) -> Response[list[float]]:
        """Create embedding for text.

        Args:
            text: Text string.

        Returns:
            Text embedding.
        """
        ...

    @operation()
    def batch_text(
        self,
        texts: list[str],
        **kwargs: Any,
    ) -> Response[list[list[float]]]:
        """Create embedding for batch of text.

        Args:
            texts: List of texts.

        Returns:
            List of text embeddings.
        """
        ...

    @operation()
    def batch_image_text(
        self,
        images: list[str | bytes | Image | ImageParam | dict],
        texts: list[str],
        **kwargs: Any,
    ) -> Response[tuple[list[list[float]], list[list[float]]]]:
        """Create embedding for batch of images and texts.

        Args:
            images: List of images.
            texts: List of texts.

        Returns:
            Tuple of list of image embeddings and text embeddings.
        """
        ...

    @operation()
    async def aembed(
        self,
        image: Image | ImageParam | dict,
        **kwargs: Any,
    ) -> Response[list[float]]:
        """Create embedding for image.

        Args:
            image: Image.

        Returns:
            Image embedding.
        """
        ...

    @operation()
    async def acompare(
        self,
        embedding1: list[float],
        embedding2: list[float],
        **kwargs,
    ) -> Response[float]:
        """Compare embeddings using cosine similarity.

        Args:
            embedding1: Embedding 1.
            embedding2: Embedding 2.

        Returns:
            Similarity score.
        """
        ...

    @operation()
    async def abatch(
        self,
        images: list[Image | ImageParam | dict],
        **kwargs: Any,
    ) -> Response[list[list[float]]]:
        """Create embedding for batch of images.

        Args:
            images: List of images.

        Returns:
            List of image embeddings.
        """
        ...

    @operation()
    async def aembed_text(
        self,
        text: str,
        **kwargs: Any,
    ) -> Response[list[float]]:
        """Create embedding for text.

        Args:
            text: Text string.

        Returns:
            Text embedding.
        """
        ...

    @operation()
    async def abatch_text(
        self,
        texts: list[str],
        **kwargs: Any,
    ) -> Response[list[list[float]]]:
        """Create embedding for batch of text.

        Args:
            texts: List of texts.

        Returns:
            List of text embeddings.
        """
        ...

    @operation()
    async def abatch_image_text(
        self,
        images: list[Image | ImageParam | dict],
        texts: list[str],
        **kwargs: Any,
    ) -> Response[tuple[list[list[float]], list[list[float]]]]:
        """Create embedding for batch of images and texts.

        Args:
            images: List of images.
            texts: List of texts.

        Returns:
            Tuple of list of image embeddings and text embeddings.
        """
        ...
