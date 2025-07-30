from typing import Any

from verse.core import Component, Response, operation

from ._models import TextToSpeechResult


class TextToSpeech(Component):
    @operation()
    def generate(
        self,
        text: str,
        speed: float | None = None,
        **kwargs: Any,
    ) -> Response[TextToSpeechResult]:
        """
        Generate speech audio from the given text.

        Args:
            text: The text input to be converted into speech.
            speech: Speech of the speech. Normal is 1.

        Returns:
            Generated speech.
        """
        ...

    @operation()
    async def agenerate(
        self,
        text: str,
        speed: float | None = None,
        **kwargs: Any,
    ) -> Response[TextToSpeechResult]:
        """
        Generate speech audio from the given text.

        Args:
            prompt (str): The text input to be converted into speech.
            speech: Speech of the speech. Normal is 1.

        Returns:
            Generated speech.
        """
        ...
