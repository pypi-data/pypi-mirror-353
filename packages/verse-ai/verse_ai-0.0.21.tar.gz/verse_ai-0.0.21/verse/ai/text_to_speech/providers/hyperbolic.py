import base64
from typing import Any

import httpx

from verse.content.audio import Audio
from verse.core import Provider, Response

from .._models import TextToSpeechResult


class Hyperbolic(Provider):
    base_url: str
    api_key: str

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.hyperbolic.xyz/v1/audio/generation",
        **kwargs,
    ):
        self.base_url = base_url
        self.api_key = api_key

    def generate(
        self,
        text: str,
        speed: float | None = None,
        **kwargs: Any,
    ) -> Response[TextToSpeechResult]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {"text": text, "speed": speed or 1}
        res = httpx.post(
            self.base_url, headers=headers, json=data, timeout=None
        ).json()
        return TextToSpeechResult(
            audio=Audio(data=base64.b64decode(res["audio"])),
        )
