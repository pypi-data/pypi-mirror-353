from typing import Any

from verse.content.audio import Audio, AudioParam
from verse.core import Component, Response, operation

from ._models import SpeechRecognitionResult


class SpeechRecognition(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @operation()
    def transcribe(
        self,
        audio: str | bytes | Audio | AudioParam | dict,
        **kwargs: Any,
    ) -> Response[SpeechRecognitionResult]:
        """Transcribe audio and convert to text.

        Args:
            audio: Audio to transcibe.

        Returns:
            Transciption result.
        """
        ...

    @operation()
    def detect_language(
        self,
        audio: str | bytes | Audio | AudioParam | dict,
        **kwargs: Any,
    ) -> Response[SpeechRecognitionResult]:
        """Detect langauge in audio.

        Args:
            audio: Audio to recognize.

        Returns:
            Detection result.
        """
        ...

    @operation()
    async def atranscribe(
        self,
        audio: str | bytes | Audio | AudioParam | dict,
        **kwargs: Any,
    ) -> Response[SpeechRecognitionResult]:
        """Transcribe audio and convert to text.

        Args:
            audio: Audio to transcibe.

        Returns:
            Transciption result.
        """
        ...

    @operation()
    async def adetect_language(
        self,
        audio: str | bytes | Audio | AudioParam | dict,
        **kwargs: Any,
    ) -> Response[SpeechRecognitionResult]:
        """Detect langauge in audio.

        Args:
            audio: Audio to recognize.

        Returns:
            Detection result.
        """
        ...
