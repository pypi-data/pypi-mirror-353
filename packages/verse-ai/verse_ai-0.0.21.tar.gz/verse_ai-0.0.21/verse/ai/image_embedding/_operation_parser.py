from verse.content.image import Image
from verse.core import OperationParser


class ImageEmbeddingOperationParser(OperationParser):
    def get_image(self) -> Image:
        image = self.get_arg("image")
        return Image.load(image)

    def get_image_as_pil(self):
        image = self.get_image()
        return image.convert("pil")

    def get_images(self) -> list[Image]:
        result = []
        images = self.get_arg("images")
        for image in images:
            result.append(Image.load(image))
        return result

    def get_images_as_pil(self):
        result = []
        images = self.get_arg("images")
        for image in images:
            result.append(Image.load(image).convert("pil"))
        return result

    def get_text(self) -> str:
        return self.get_arg("text")

    def get_texts(self) -> list[str]:
        return self.get_arg("texts")

    def get_embedding1(self) -> list[float]:
        return self.get_arg("embedding1")

    def get_embedding2(self) -> list[float]:
        return self.get_arg("embedding2")
