import asyncio
import json
import logging
import time
from typing import Any, Union

import httpx

from verse.content.image import Image
from verse.content.video import Video
from verse.core import Provider

from .._models import VideoGenerationResult


class Hailuoai(Provider):
    def __init__(
        self,
        api_key: str = "",
        **kwargs,
    ):
        self.api_key = api_key

    def generate(
        self, prompt: str, key_frames: list[Union[Image, None]], **kwargs: Any
    ):
        model = kwargs.get("model", "video-01")

        task_id = self._invoke_video_generation(model, prompt)
        file_id = self._wait_for_task_completion(task_id)

        return self._fetch_video_result(file_id)

    async def agenerate(
        self, prompt: str, key_frames: list[Union[Image, None]], **kwargs: Any
    ):
        model = kwargs.get("model", "video-01")

        task_id = await self._ainvoke_video_generation(model, prompt)
        file_id = await self._await_for_task_completion(task_id)
        return await self._afetch_video_result(file_id)

    def _invoke_video_generation(self, model: str, prompt: str) -> str:
        url = "https://api.minimaxi.chat/v1/video_generation"
        payload = json.dumps({"prompt": prompt, "model": model})

        response = httpx.request(
            "POST",
            url,
            headers=self._get_headers(),
            data=payload,
        )

        assert (
            response.status_code == 200
        ), f"Failed to submit video generation - status code: {response.status_code}"

        response = response.json()

        status_code = response.get("base_resp", {}).get("status_code", 0)
        assert (
            status_code == 0
        ), f"Failed to invoke video generation - status code: {status_code}"

        return response["task_id"]

    def _wait_for_task_completion(self, task_id: str) -> str:
        url = (
            "https://api.minimaxi.chat/v1/query/video_generation?task_id="
            + task_id
        )

        while True:
            try:
                response = httpx.request(
                    "GET",
                    url,
                    headers=self._get_headers(),
                )
                status = response.json()["status"]
            except Exception as e:
                logging.error(f"Error getting status: {e}")
                time.sleep(5)
                continue

            if status == "Success":
                return response.json()["file_id"]

            if status == "Fail":
                raise Exception("Video generation failed")

            time.sleep(5)

    def _fetch_video_result(self, file_id: str):
        url = "https://api.minimaxi.chat/v1/files/retrieve?file_id=" + file_id
        response = httpx.request("GET", url, headers=self._get_headers())

        video_url = response.json()["file"]["download_url"]
        logging.info("Video download link: " + video_url)

        for _ in range(3):
            response = httpx.get(video_url)
            if response.status_code == 200:
                break

            time.sleep(3)

        return VideoGenerationResult(
            video=Video(data=response.content, url=video_url),
        )

    async def _ainvoke_video_generation(self, model: str, prompt: str) -> str:
        """
        Asynchronous function to invoke video generation.

        Args:
        - model (str): The video generation model to use.
        - prompt (str): The prompt to generate a video for.

        Returns:
        - task_id (str): The ID of the submitted video generation task.
        """
        url = "https://api.minimaxi.chat/v1/video_generation"
        payload = json.dumps({"prompt": prompt, "model": model})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self._get_headers(),
                data=payload,
            )

            assert (
                response.status_code == 200
            ), f"Failed to submit video generation - status code: {response.status_code}"

            response = response.json()

            status_code = response.get("base_resp", {}).get("status_code", 0)
            assert (
                status_code == 0
            ), f"Failed to invoke video generation - status code: {status_code}"

            return response["task_id"]

    async def _await_for_task_completion(self, task_id: str) -> str:
        """
        Asynchronously waits for a video generation task to complete.

        Args:
        - task_id (str): ID of the task to wait for.

        Returns:
        - str: File ID of the generated video upon successful completion.

        Raises:
        - Exception: If video generation fails.
        """
        url = (
            "https://api.minimaxi.chat/v1/query/video_generation?task_id="
            + task_id
        )

        while True:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url,
                        headers=self._get_headers(),
                    )
                response.raise_for_status()  # Raises an exception for bad status codes
                status = response.json()["status"]
            except httpx.RequestError as e:
                logging.error(f"Error getting status: {e}")
                await asyncio.sleep(5)
                continue
            except Exception as e:
                logging.error(f"Error processing response: {e}")
                await asyncio.sleep(5)
                continue

            if status == "Success":
                return response.json()["file_id"]

            if status == "Fail":
                raise Exception("Video generation failed")

            await asyncio.sleep(5)

    async def _afetch_video_result(
        self, file_id: str
    ) -> VideoGenerationResult:
        """
        Async function to fetch video result.

        Args:
        - file_id (str): The ID of the file to retrieve.

        Returns:
        - VideoGenerationResult: The result of the video generation.
        """
        url = "https://api.minimaxi.chat/v1/files/retrieve?file_id=" + file_id

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._get_headers())

        video_url = response.json()["file"]["download_url"]
        logging.info("Video download link: " + video_url)

        for _ in range(3):
            async with httpx.AsyncClient() as client:
                response = await client.get(video_url)
                if response.status_code == 200:
                    break
                await asyncio.sleep(3)

        return VideoGenerationResult(
            video=Video(data=response.content, url=video_url),
        )

    def _get_headers(self):
        return {
            "authorization": "Bearer " + self.api_key,
            "content-type": "application/json",
        }
