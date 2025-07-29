from verse.content.video import Video
from verse.core import DataModel


class VideoGenerationResult(DataModel):
    """
    Represents the result of a video generation process.

    Attributes:
        video (Video): The generated video.
    """

    video: Video
