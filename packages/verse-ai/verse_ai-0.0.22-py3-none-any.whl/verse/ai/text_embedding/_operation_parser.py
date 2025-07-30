from verse.core import OperationParser


class TextEmbeddingOperationParser(OperationParser):
    def get_texts(self) -> list[str]:
        texts = self.get_arg("texts")
        if isinstance(texts, str):
            return [texts]
        return texts

    def get_embedding1(self) -> list[float]:
        return self.get_arg("embedding1")

    def get_embedding2(self) -> list[float]:
        return self.get_arg("embedding2")
