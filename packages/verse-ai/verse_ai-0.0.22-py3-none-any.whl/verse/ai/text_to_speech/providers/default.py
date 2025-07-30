import httpx
import io
import os
import torch
import soundfile as sf
from typing import Any
from verse.content.audio import Audio
from verse.core import Provider, Response

from .._models import TextToSpeechResult
from .kokoro.models import build_model
from .kokoro.kokoro import generate as kokoro_generate

class Default(Provider):
    MODEL_FILE_NAME = "kokoro-v0_19.pth"
    VOICE_NAMES = [
        'af', # Default voice is a 50-50 mix of Bella & Sarah
        'af_bella', 'af_sarah', 'am_adam', 'am_michael',
        'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
        'af_nicole', 'af_sky',
    ]
    
    def __init__(
        self
    ):
        try:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

            if not os.path.exists(self.MODEL_FILE_NAME):            
                url = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v0_19.pth"
                print(f"Download model from {url}")
                response = httpx.get(url, timeout=600, verify=False, follow_redirects=True)
                assert response.status_code == 200, f"Failed to download model from {url} - status: {response.status_code}"
                with open(self.MODEL_FILE_NAME, "wb") as f:
                    f.write(response.content)

            self.model = build_model(self.MODEL_FILE_NAME, self.device)
            self.voices = {}
            for voice_name in self.VOICE_NAMES:
                voice_path = f"{voice_name}.pt"
                if not os.path.exists(voice_path):
                    # download voice if not existed
                    url = f"https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/{voice_name}.pt"
                    print(f"Download voice from {url}")
                    response = httpx.get(url, timeout=600, verify=False, follow_redirects=True)
                    with open(voice_path, "wb") as f:
                        f.write(response.content)

                self.voices[voice_name] = torch.load(voice_path, weights_only=True).to(self.device)
        except Exception as e:
            print("""If you have not installed Kokoro-TTS, please follow below instructions:
```
sudo apt-get -y install espeak-ng
pip install -q phonemizer torch transformers scipy munch 
```
                  
More info at: https://huggingface.co/hexgrad/Kokoro-82M
""")
            raise e

    def generate(
        self,
        text: str,
        speed: float | None = None,
        **kwargs: Any,
    ) -> Response[TextToSpeechResult]:
        voice = kwargs.get("voice", "af")
        assert voice in self.VOICE_NAMES, f"voice must be one of these: {self.VOICE_NAMES}"

        audio, _ = kokoro_generate(self.model, text, self.voices[voice], lang="a")
        
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, audio, 24000, format="wav")

        return TextToSpeechResult(
            audio=Audio(data=audio_buffer.getvalue()),
        )