from verse.core import DataModel


class Usage(DataModel):
    prompt_tokens: int
    """Number of tokens in the prompt."""

    total_tokens: int
    """Total number of tokens used by the request."""


class TextEmbeddingResult(DataModel):
    embeddings: list[list[float]]
    """List of embeddings."""

    model: str | None = None
    """The model used for the embedding."""

    usage: Usage | None = None
    """Usage statistics for the embedding request."""
