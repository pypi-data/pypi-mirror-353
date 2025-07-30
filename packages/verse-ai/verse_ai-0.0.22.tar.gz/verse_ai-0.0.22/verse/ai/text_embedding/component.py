from typing import Any

from verse.core import Component, Response, operation

from ._models import TextEmbeddingResult


class TextEmbedding(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @operation()
    def embed(
        self,
        texts: str | list[str],
        **kwargs: Any,
    ) -> Response[TextEmbeddingResult]:
        """Create embedding for text.

        Args:
            texts: Texts to embed.

        Returns:
            Text embeddings.
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
    async def aembed(
        self,
        texts: str | list[str],
        **kwargs: Any,
    ) -> Response[TextEmbeddingResult]:
        """Create embedding for text.

        Args:
            texts: Texts to embed.

        Returns:
            Text embeddings.
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
