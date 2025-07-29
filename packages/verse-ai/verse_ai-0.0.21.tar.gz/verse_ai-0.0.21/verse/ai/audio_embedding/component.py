from typing import Any

from verse.content.audio import Audio, AudioParam
from verse.core import Component, Response, operation


class AudioEmbedding(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @operation()
    def embed(
        self,
        audio: str | bytes | Audio | AudioParam | dict,
        **kwargs: Any,
    ) -> Response[list[float]]:
        """Create embedding for audio.

        Args:
            audio: Audio.

        Returns:
            Audio embedding.
        """
        ...

    @operation()
    def compare(
        self,
        embedding1: list[float],
        embedding2: list[float],
        dist_metric: str = "cosine",
        **kwargs,
    ) -> Response[float]:
        """Compare embeddings using cosine similarity.

        Args:
            embedding1: Embedding 1.
            embedding2: Embedding 2.

        Returns:
            Score defined by dist_metric.
        """
        ...

    @operation()
    def batch(
        self,
        audios: list[bytes | Audio | Audio | dict],
        **kwargs: Any,
    ) -> Response[list[list[float]]]:
        """Create embedding for batch of audios.

        Args:
            audios: List of audios.

        Returns:
            List of audio embeddings.
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
            text: Text.

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
        """Create embedding for batch of texts.

        Args:
            texts: List of texts.

        Returns:
            List of text embeddings.
        """
        ...

    @operation()
    def batch_audio_text(
        self,
        audios: list[bytes | Audio | AudioParam | dict],
        texts: list[str],
        **kwargs: Any,
    ) -> Response[list[list[float]]]:
        """Create embedding for batch of audio and text.

        Args:
            audios: List of audios.
            texts: List of texts.

        Returns:
            List of audio-text embeddings.
        """
        ...

    @operation()
    async def aembed(
        self,
        audio: bytes | Audio | AudioParam | dict,
        **kwargs: Any,
    ) -> Response[list[float]]:
        """Create embedding for audio.

        Args:
            audio: Audio.

        Returns:
            Audio embedding.
        """
        ...

    @operation()
    async def acompare(
        self,
        embedding1: list[float],
        embedding2: list[float],
        dist_metric: str = "cosine",
        **kwargs,
    ) -> Response[float]:
        """Compare embeddings using cosine similarity.

        Args:
            embedding1: Embedding 1.
            embedding2: Embedding 2.

        Returns:
            Score defined by dist_metric.
        """
        ...

    @operation()
    async def abatch(
        self,
        audios: list[bytes | Audio | Audio | dict],
        **kwargs: Any,
    ) -> Response[list[list[float]]]:
        """Create embedding for batch of audios.

        Args:
            audios: List of audios.

        Returns:
            List of audio embeddings.
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
            text: Text.

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
        """Create embedding for batch of texts.

        Args:
            texts: List of texts.

        Returns:
            List of text embeddings.
        """
        ...

    @operation()
    async def abatch_audio_text(
        self,
        audios: list[bytes | Audio | AudioParam | dict],
        texts: list[str],
        **kwargs: Any,
    ) -> Response[list[list[float]]]:
        """Create embedding for batch of audio and text.

        Args:
            audios: List of audios.
            texts: List of texts.

        Returns:
            List of audio-text embeddings.
        """
        ...
