from verse.content.audio import Audio, AudioParam
from verse.core import OperationParser


class SpeechRecognitionOperationParser(OperationParser):
    def get_audio(self) -> Audio:
        audio = self.get_arg("audio")
        return SpeechRecognitionOperationParser.normalize_audio(audio)

    @staticmethod
    def normalize_audio(audio) -> Audio:
        if isinstance(audio, str):
            return Audio(path=audio)
        elif isinstance(audio, bytes):
            return Audio(data=audio)
        elif isinstance(audio, dict):
            return Audio(param=AudioParam.from_dict(audio))
        elif isinstance(audio, AudioParam):
            return Audio(param=audio)
        return audio
