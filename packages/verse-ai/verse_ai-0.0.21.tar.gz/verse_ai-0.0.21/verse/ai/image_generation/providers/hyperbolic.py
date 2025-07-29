import base64
from typing import Any

import httpx

from verse.content.image import Image, ImageParam
from verse.core import Provider, Response

from .._models import ImageGenerationResult


class Hyperbolic(Provider):
    base_url: str
    api_key: str
    model: str

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.hyperbolic.xyz/v1/image/generation",
        model: str = "SD2",
        **kwargs,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        reference_image: str | bytes | Image | ImageParam | dict | None = None,
        width: int = 1024,
        height: int = 1024,
        **kwargs: Any,
    ) -> Response[ImageGenerationResult]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model_name": self.model,
            "prompt": prompt,
            "steps": kwargs.get("steps", 30),
            "cfg_scale": kwargs.get("cfg_scale", 5),
            "enable_refiner": kwargs.get("enable_refiner", False),
            "height": width,
            "width": height,
            "backend": "auto",
        }
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if reference_image:
            data["enable_reference"] = True
            data["image"] = Image.load(reference_image).convert(type="base64")
        res = httpx.post(
            self.base_url, headers=headers, json=data, timeout=None
        ).json()
        try:
            images: list = []
            for image in res["images"]:
                images.append(Image(data=base64.b64decode(image["image"])))
            return Response(result=ImageGenerationResult(images=images))
        except Exception as e:
            print(res)
            raise e
