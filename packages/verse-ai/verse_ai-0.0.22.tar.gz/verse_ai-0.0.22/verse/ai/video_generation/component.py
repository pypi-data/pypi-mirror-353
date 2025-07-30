from typing import Any, Union

from verse.content.image import Image
from verse.core import Component, Response, operation

from ._models import VideoGenerationResult


class VideoGeneration(Component):
    @operation()
    def generate(
        self,
        prompt: str,
        key_frames: list[Union[Image, None]] = [],
        **kwargs: Any
    ) -> Response[VideoGenerationResult]:
        """
        Generate a video from a given text prompt.

        Args:
            prompt (str): The text prompt to generate the video from.
            key_frames (list[Image]): Optional list of key frames
                to guide the video generation.
                If empty, generate video using only the prompt.
                Defaults to an empty list.
            **kwargs (Any): Additional keyword arguments for video generation.

        Returns:
            VideoGenerationResult: The result of the video generation process.
        """
        ...

    @operation()
    async def agenerate(
        self,
        prompt: str,
        key_frames: list[Union[Image, None]] = [],
        **kwargs: Any
    ) -> Response[VideoGenerationResult]:
        """
        Asynchronously generate a video from a given text prompt.

        Args:
            prompt (str): The text prompt to generate the video from.
            key_frames (list[Image]): Optional list of key frames
                to guide the video generation.
                If empty, generate video using only the prompt.
                Defaults to an empty list.
            **kwargs (Any): Additional keyword arguments for video generation.

        Returns:
            VideoGenerationResult: The result of the video generation process.
        """
        ...
