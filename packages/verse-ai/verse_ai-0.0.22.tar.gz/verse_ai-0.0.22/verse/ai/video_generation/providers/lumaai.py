import asyncio
import time
from typing import Any, Optional, Union

import httpx

try:
    from lumaai import NOT_GIVEN, AsyncLumaAI, LumaAI
except:
    assert False, "lumaai package not found. Please install using 'pip install lumaai'"

from verse.content.image import Image
from verse.content.video import Video
from verse.core import Provider

from .._models import VideoGenerationResult


class Lumaai(Provider):
    def __init__(
        self,
        api_key: str = "",
        **kwargs,
    ):
        self.api_key = api_key

    def generate(
        self, prompt: str, key_frames: list[Union[Image, None]], **kwargs: Any
    ):
        client = LumaAI(auth_token=self.api_key)

        key_frames_dict = self._get_keyframes(key_frames)
        if key_frames_dict is None:
            key_frames_dict = NOT_GIVEN

        aspect_ratio = self._get_aspect_ratio(**kwargs)
        generation = client.generations.create(
            prompt=prompt, aspect_ratio=aspect_ratio, keyframes=key_frames_dict
        )

        completed = False
        while not completed:
            generation = client.generations.get(id=generation.id)
            if generation.state == "completed":
                completed = True
            elif generation.state == "failed":
                raise RuntimeError(
                    f"Generation failed: {generation.failure_reason}"
                )

            time.sleep(3)

        # download the video
        video_url = generation.assets.video
        for _ in range(3):
            response = httpx.get(video_url)
            if response.status_code == 200:
                break

            time.sleep(3)

        assert (
            response.status_code == 200
        ), f"Failed to download from {video_url} - status code: {response.status_code}"

        return VideoGenerationResult(
            video=Video(data=response.content, url=video_url),
        )

    async def agenerate(
        self, prompt: str, key_frames: list[Union[Image, None]], **kwargs: Any
    ):
        client = AsyncLumaAI(auth_token=self.api_key)

        key_frames_dict = self._get_keyframes(key_frames)
        if key_frames_dict is None:
            key_frames_dict = NOT_GIVEN

        aspect_ratio = self._get_aspect_ratio(**kwargs)

        generation = await client.generations.create(
            prompt=prompt, aspect_ratio=aspect_ratio, keyframes=key_frames_dict
        )

        generation_id = generation.id
        completed = False
        while not completed:
            generation = await client.generations.get(id=generation_id)
            if generation.state == "completed":
                completed = True
            elif generation.state == "failed":
                raise RuntimeError(
                    f"Generation failed: {generation.failure_reason}"
                )

            await asyncio.sleep(3)

        # download the video
        video_url = generation.assets.video
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

    def _get_aspect_ratio(self, **kwargs: Any) -> str:
        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        assert aspect_ratio in [
            "1:1",
            "16:9",
            "9:16",
            "4:3",
            "3:4",
            "21:9",
            "9:21",
        ], 'aspect_ratio must be in \
            ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]'

        return aspect_ratio

    def _get_keyframes(
        self, key_frames: list[Union[Image, None]]
    ) -> Optional[dict]:
        assert (
            len(key_frames) <= 2
        ), "LumaAI only supports up to 2 key frames. \
            One as starting frame and One as ending frame."

        if len(key_frames) == 0:
            return None

        key_frames_dict = {}

        if key_frames[0] is not None:
            assert (
                key_frames[0].url != ""
            ), "key_frames[0].url must not be empty"

            key_frames_dict["frame0"] = {
                "type": "image",
                "url": key_frames[0].url,
            }

        if len(key_frames) == 2 and key_frames[1] is not None:
            assert (
                key_frames[1].url != ""
            ), "key_frames[1].url must not be empty"

            key_frames_dict["frame1"] = {
                "type": "image",
                "url": key_frames[1].url,
            }

        return key_frames_dict
