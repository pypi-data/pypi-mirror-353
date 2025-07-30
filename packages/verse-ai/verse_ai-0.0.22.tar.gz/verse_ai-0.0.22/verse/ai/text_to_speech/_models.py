from verse.content.audio import Audio
from verse.core import DataModel


class TextToSpeechResult(DataModel):
    """
    TextToSpeechResult is a data model representing
    the result of a text-to-speech operation.
    """

    audio: Audio
