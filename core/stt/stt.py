from core.stt.groq_client import GroqSTT
from typing import Tuple


class STT:
    def __init__(self, model_id: str = "whisper-large-v3", language: str = "en"):
        self.model_id = model_id
        self.models = {
            "GROQ": [
                ("Whisper Large", "whisper-large-v3"),
                ("Whisper Medium", "whisper-medium-v3"),
                ("Whisper Small", "whisper-small-v3"),
            ]
        }
        self.language = language

    def list_models(self):
        return self.models
    
    def model_enum(self, model_name: str) -> Tuple[str, str]:
        model_dict = {
            model[0]: (model_enum, model[1]) 
            for model_enum, models in self.models.items() 
            for model in models
        }
        return model_dict.get(model_name, (None, None))

    def transcribe(self, audio_file: str) -> str:
        model_enum, model_id = self.model_enum(self.model_id)
        if model_enum == "GROQ":
            return GroqSTT(model_id, language=self.language).transcribe(audio_file)
        