from verse.content.audio import Audio, AudioParam
from verse.core import OperationParser


class AudioEmbeddingOperationParser(OperationParser):
    def get_audio(self) -> Audio:
        audio = self.get_arg("audio")
        return self._normalize_audio(audio)
    
    def get_audios(self) -> list[Audio]:
        result = []
        audios = self.get_arg("audios")
        for audio in audios:
            result.append(self._normalize_audio(audio))
        return result
    
    def _normalize_audio(self, audio) -> Audio:
        if isinstance(audio, str):
            return Audio(path=audio)
        elif isinstance(audio, bytes):
            return Audio(data=audio)
        elif isinstance(audio, dict):
            return Audio(param=AudioParam.from_dict(audio))
        elif isinstance(audio, AudioParam):
            return Audio(param=audio)
        return audio
    
    def get_text(self) -> str:
        return self.get_arg("text")

    def get_texts(self) -> list[str]:
        return self.get_arg("texts")

    def get_embedding1(self) -> list[float]:
        return self.get_arg("embedding1")

    def get_embedding2(self) -> list[float]:
        return self.get_arg("embedding2")
    
    def get_dist_metric(self) -> str:
        return self.get_arg("dist_metric")