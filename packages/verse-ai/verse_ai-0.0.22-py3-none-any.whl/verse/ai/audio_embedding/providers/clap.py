"""
Audio embedding provider using CLAP model.
"""

__all__ = ["Clap"]

from typing import Any

import numpy as np
import torch
from transformers import AutoFeatureExtractor, AutoProcessor, ClapModel

from verse.content.audio import Audio
from verse.core import Context, Operation, Provider, Response

from .._operation import AudioEmbeddingOperation
from .._operation_parser import AudioEmbeddingOperationParser


class Clap(Provider):
    model: str
    device: str | None

    _device: Any
    _model: Any
    _processor: Any

    def __init__(
        self,
        model: str = "laion/clap-htsat-fused",
        device: str | None = None,
        **kwargs,
    ):
        """Intialize.

        Args:
            model:
                CLAP model name.
            device:
                Pytorch device name.
        """
        self.model = model
        self.device = device

        self._model = None
        self._device = None
        self._processor = None

    def __setup__(self, context: Context | None = None) -> None:
        if self._model:
            return
        self._device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        if self.device is not None:
            self._device = self.device
        self._model = ClapModel.from_pretrained(self.model).to(self._device)
        self._processor = AutoProcessor.from_pretrained(self.model)

    def __run__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Response:
        self.__setup__()
        op_parser = AudioEmbeddingOperationParser(operation)

        if op_parser.op_equals(AudioEmbeddingOperation.EMBED):
            result = self._embed(audio=op_parser.get_audio())
        elif op_parser.op_equals(AudioEmbeddingOperation.EMBED_TEXT):
            result = self._embed_text(text=op_parser.get_text())
        elif op_parser.op_equals(AudioEmbeddingOperation.BATCH):
            result = self._batch(audios=op_parser.get_audios())
        elif op_parser.op_equals(AudioEmbeddingOperation.BATCH_TEXT):
            result = self._batch_text(texts=op_parser.get_texts())
        elif op_parser.op_equals(AudioEmbeddingOperation.BATCH_AUDIO_TEXT):
            result = self._batch_audio_text(
                audios=op_parser.get_audios(), texts=op_parser.get_texts()
            )
        elif op_parser.op_equals(AudioEmbeddingOperation.COMPARE):
            result = self._compare(
                embedding1=torch.Tensor(op_parser.get_embedding1()),
                embedding2=torch.Tensor(op_parser.get_embedding2()),
                dist_metric=op_parser.get_dist_metric(),
            )
        else:
            return super().__run__(operation, **kwargs)

        return Response(result=result)

    def _embed(
        self,
        audio: Audio,
        **kwargs: Any,
    ):
        audio = self._preprocess_audio(audio)

        inputs = self._processor(
            audios=audio,
            return_tensors="pt",
            padding=True,
            sampling_rate=48000,
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model.get_audio_features(**inputs)

        result = outputs.cpu().numpy().flatten().tolist()
        return result

    def _embed_text(
        self,
        text: str,
        **kwargs: Any,
    ):
        inputs = self._processor(
            text=text, return_tensors="pt", padding=True
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model.get_text_features(**inputs)

        result = outputs.cpu().numpy().flatten().tolist()
        return result

    def _batch(
        self,
        audios: list[Audio],
        **kwargs: Any,
    ):
        audios = [self._preprocess_audio(audio) for audio in audios]

        inputs = self._processor(
            audios=audios,
            return_tensors="pt",
            padding=True,
            sampling_rate=48000,
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model.get_audio_features(**inputs)

        result = outputs.cpu().numpy().tolist()
        return result

    def _batch_text(
        self,
        texts: list[str],
        **kwargs: Any,
    ):
        inputs = self._processor(
            text=texts, return_tensors="pt", padding=True
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model.get_text_features(**inputs)

        result = outputs.cpu().numpy().tolist()
        return result

    def _batch_audio_text(
        self,
        audios: list[Audio],
        texts: list[str],
        **kwargs: Any,
    ):
        audios = [self._preprocess_audio(audio) for audio in audios]

        inputs = self._processor(
            text=texts,
            audios=audios,
            return_tensors="pt",
            padding=True,
            sampling_rate=48000,
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model(**inputs)

        result = [
            outputs.audio_embedding.cpu().numpy().tolist(),
            outputs.text_embedding.cpu().numpy().tolist(),
        ]
        return result

    def _compare(
        self,
        embedding1,
        embedding2,
        dist_metric: str = "cosine",
        **kwargs,
    ):
        """
        Compare embeddings using cosine similarity.
        embedding1: shape (n, d) where n is the number of embeddings and d is the dimension of the embeddings
        embedding2: shape (m, d) where m is the number of embeddings and d is the dimension of the embeddings
        dist_metric: distance metric to use. Currently only "cosine" is supported
        output: shape (n, m) where output[i, j] is the similarity between embedding1[i] and embedding2[j]
        """
        if dist_metric != "cosine":
            raise ValueError(f"Unsupported distance metric: {dist_metric}")
        if embedding1.shape[-1] != embedding2.shape[-1]:
            raise ValueError("Embeddings must have the same dimension")
        norm1 = torch.linalg.vector_norm(
            embedding1, ord=2, dim=-1, keepdim=True
        )
        norm2 = torch.linalg.vector_norm(
            embedding2, ord=2, dim=-1, keepdim=True
        )

        similarity = embedding1 @ embedding2.T / (norm1 * norm2.T)

        # TODO: add support for other distance metrics

        return similarity.cpu().numpy().tolist()

    def _preprocess_audio(self, audio: Audio):
        audio = audio.convert(
            type="bytes",
            format="wav",
            codec="pcm_s16le",
            rate=16000,
            channels=1,
        )
        array = np.frombuffer(audio, dtype=np.int16)
        array = array.astype(np.float32) / 32768.0

        return array
