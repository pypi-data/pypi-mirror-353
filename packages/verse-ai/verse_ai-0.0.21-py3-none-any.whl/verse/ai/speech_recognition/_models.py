from typing import Any

from verse.core import DataModel


class SpeechRecognitionResult(DataModel):
    """Speech recognition result."""

    text: str | None = None
    language: str | None = None
    verbose: Any | None = None
    """Transcribed text."""
