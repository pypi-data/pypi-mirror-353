import asyncio
import base64
import time
from typing import Any, Optional, Union

import httpx

try:
    from runwayml import AsyncRunwayML, RunwayML
except:
    assert (
        False
    ), "runwayml package not found. Please install using 'pip install runwayml'"

from verse.content.image import Image
from verse.content.video import Video
from verse.core import Provider

from .._models import VideoGenerationResult


class Runwayml(Provider):
    def __init__(self, api_key: str = "", **kwargs):
        self.api_key = api_key

    def generate(
        self, prompt: str, key_frames: list[Union[Image, None]], **kwargs: Any
    ):
        client = RunwayML(api_key=self.api_key)
        assert (
            len(key_frames) == 1
        ), "RunwayAI only supports image to video generation."

        model = kwargs.get("model", "gen3a_turbo")
        duration = kwargs.get("duration", 5)
        ratio = kwargs.get("ratio", "1280:768")
        seed = kwargs.get("seed", 123)
        watermark = kwargs.get("watermark", False)

        prompt_image = self._get_prompt_image(key_frames[0])
        task = client.image_to_video.create(
            model=model,
            duration=duration,
            ratio=ratio,
            seed=seed,
            watermark=watermark,
            prompt_image=prompt_image,
            prompt_text=prompt,
        )
        task_id = task.id

        time.sleep(1)
        task = client.tasks.retrieve(task_id)
        while task.status not in ["SUCCEEDED", "FAILED"]:
            time.sleep(5)
            task = client.tasks.retrieve(task_id)

        video_url = task.output[0]
        for _ in range(3):
            response = httpx.get(video_url)
            if response.status_code == 200:
                break

        assert (
            response.status_code == 200
        ), f"Failed to download from {video_url} - status code: {response.status_code}"

        return VideoGenerationResult(
            video=Video(data=response.content, url=video_url)
        )

    async def agenerate(
        self, prompt: str, key_frames: list[Union[Image, None]], **kwargs: Any
    ):
        client = AsyncRunwayML(api_key=self.api_key)
        assert (
            len(key_frames) == 1
        ), "RunwayAI only supports image to video generation."

        model = kwargs.get("model", "gen3a_turbo")
        duration = kwargs.get("duration", 5)
        ratio = kwargs.get("ratio", "1280:768")
        seed = kwargs.get("seed", 123)
        watermark = kwargs.get("watermark", False)

        prompt_image = self._get_prompt_image(key_frames[0])
        task = await client.image_to_video.create(
            model=model,
            duration=duration,
            ratio=ratio,
            seed=seed,
            watermark=watermark,
            prompt_image=prompt_image,
            prompt_text=prompt,
        )
        task_id = task.id

        task = await client.tasks.retrieve(task_id)
        while task.status not in ["SUCCEEDED", "FAILED"]:
            await asyncio.sleep(5)
            task = await client.tasks.retrieve(task_id)

        video_url = task.output[0]
        for _ in range(3):
            async with httpx.AsyncClient() as httpx_client:
                response = await httpx_client.get(video_url)
                if response.status_code == 200:
                    break

        assert (
            response.status_code == 200
        ), f"Failed to download from {video_url} - status code: {response.status_code}"

        return VideoGenerationResult(
            video=Video(data=response.content, url=video_url),
        )

    def _get_prompt_image(self, image: Image) -> str:
        if image.url is not None:
            return image.url
        elif image.base64 is not None:
            return image.base64
        elif image.path is not None:
            with open(image.path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        else:
            assert (
                False
            ), "image should have one of url/base64/path properties."
