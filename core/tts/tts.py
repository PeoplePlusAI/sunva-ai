from core.tts.coqui_client import CoquiTTS
from typing import Tuple

class TTS:
    def __init__(self, language: str = "en"):
        self.language = language
        self.models = {
            "coqui": {
                "en": "tts_models/en/ljspeech/tacotron2-DDC",  # Default English model
                # Add more language mappings here
            }
        }
        self.model_id, self.model_enum = self._select_model()

    def _select_model(self) -> Tuple[str, str]:
        for model_enum, lang_models in self.models.items():
            if self.language in lang_models:
                return lang_models[self.language], model_enum
        raise ValueError(f"Unsupported language: {self.language}")

    def list_models(self):
        return self.models
    
    def speech(self, text: str) -> bytes:
        if self.model_enum == "coqui":
            return CoquiTTS(self.model_id, language=self.language).speech(text)
        else:
            return None