from typing import Any

from verse.content.image import Image, ImageParam
from verse.core import Component, Response, operation

from ._models import ImageGenerationResult


class ImageGeneration(Component):
    @operation()
    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        reference_image: str | bytes | Image | ImageParam | dict | None = None,
        width: int = 1024,
        height: int = 1024,
        **kwargs: Any,
    ) -> Response[ImageGenerationResult]:
        """
        Generate image from the given prompt.

        Args:
            prompt:
                The text prompt to generate image.
            negative_prompt:
                Prompt on what not to include.
            reference_image:
                Reference image for generation.
            width:
                Width of the image.
            height:
                Height of the image.
            steps (int):
                The number of denoising steps or iterations the
                model uses to generate the image from the initial noise.
            cfg_scale (float):
                Controls the strength of the guidance applied to
                steer the generation process toward the given text prompt.
            enable_refiner (bool):
                Toggles the use of a "refiner" model,
                which is a secondary process designed to enhance the quality,
                details, or resolution of the initial generated image.

        Returns:
            Generated image.
        """
        ...

    @operation()
    async def agenerate(
        self,
        prompt: str,
        negative_prompt: str = "",
        reference_image: str | bytes | Image | ImageParam | dict | None = None,
        width: int = 1024,
        height: int = 1024,
        **kwargs: Any,
    ) -> Response[ImageGenerationResult]:
        """
        Generate image from the given prompt.

        Args:
            prompt:
                The text prompt to generate image.
            negative_prompt:
                Prompt on what not to include.
            reference_image:
                Reference image for generation.
            width:
                Width of the image.
            height:
                Height of the image.
            steps (int):
                The number of denoising steps or iterations the
                model uses to generate the image from the initial noise.
            cfg_scale (float):
                Controls the strength of the guidance applied to
                steer the generation process toward the given text prompt.
            enable_refiner (bool):
                Toggles the use of a "refiner" model,
                which is a secondary process designed to enhance the quality,
                details, or resolution of the initial generated image.

        Returns:
            Generated image.
        """
        ...
