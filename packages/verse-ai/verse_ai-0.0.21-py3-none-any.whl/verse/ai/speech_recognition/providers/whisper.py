"""
Speech recognition using Whisper.
"""

__all__ = ["Whisper"]

import functools
from typing import Any

import av
import numpy as np
import whisper
from whisper import Whisper as OpenAIWhisper

from verse.content.audio import Audio, AudioParam
from verse.core import Context, Provider, Response

from .._models import SpeechRecognitionResult
from .._operation_parser import SpeechRecognitionOperationParser

whisper.torch.load = functools.partial(whisper.torch.load, weights_only=True)


class Whisper(Provider):
    model: str
    device: str | None
    fp16: bool

    _model: OpenAIWhisper

    def __init__(
        self,
        model: str = "tiny",
        device: str | None = None,
        fp16: bool = False,
        **kwargs,
    ):
        """Intialize.

        Args:
            model:
                Whisper model name.
            device:
                Pytorch device name.
            fp16:
                fp16 option.
        """
        self.model = model
        self.device = device
        self.fp16 = fp16
        self._model = None

    def __setup__(self, context: Context | None = None) -> None:
        if self._model:
            return
        self._model = whisper.load_model(name=self.model, device=self.device)

    def transcribe(
        self,
        audio: str | bytes | Audio | AudioParam | dict,
        **kwargs: Any,
    ) -> Response[SpeechRecognitionResult]:
        naudio = SpeechRecognitionOperationParser.normalize_audio(audio)
        waudio = self._extract_and_resample_audio(
            naudio.convert(type="stream")
        )
        waudio = whisper.pad_or_trim(waudio)
        result = whisper.transcribe(self._model, waudio, fp16=self.fp16)
        result = SpeechRecognitionResult(
            text=result["text"], language=result["language"], verbose=result
        )
        return Response(result=result)

    def detect_language(
        self,
        audio: str | bytes | Audio | AudioParam | dict,
        **kwargs: Any,
    ) -> Response[SpeechRecognitionResult]:
        naudio = SpeechRecognitionOperationParser.normalize_audio(audio)
        waudio = self._extract_and_resample_audio(
            naudio.convert(type="stream")
        )
        waudio = whisper.pad_or_trim(waudio)
        mel = whisper.log_mel_spectrogram(waudio).to(self._model.device)
        _, probs = self._model.detect_language(mel)
        return Response(
            result=SpeechRecognitionResult(language=max(probs, key=probs.get))
        )

    def _extract_and_resample_audio(self, stream, target_rate=16000):
        container = av.open(stream)
        stream = container.streams.audio[0]

        resampler = av.audio.resampler.AudioResampler(
            format="s16", layout="mono", rate=target_rate
        )

        samples = []

        for frame in container.decode(stream):
            resampled_frames = resampler.resample(frame)
            for resampled_frame in resampled_frames:
                samples.append(resampled_frame.to_ndarray())

        audio_data = np.concatenate(samples, axis=1)
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=0)

        audio_data = audio_data / np.max(np.abs(audio_data))
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        return audio_data
