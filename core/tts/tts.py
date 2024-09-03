from core.tts.coqui_client import CoquiTTS
from core.tts.ai4bharat_client import Ai4BharatTTS

from typing import Tuple

class TTS:
    def __init__(self, model_name: str, language: str = "en"):
        self.model = model_name
        self.language = language
        self.models = {
            "coqui": [
                ("coqui-tacotron2", "tts_models/en/ljspeech/tacotron2-DDC"),
                ("coqui-glow-tts", "tts_models/en/ljspeech/glow-tts"),
                ("coqui-waveglow", "tts_models/en/ljspeech/waveglow"),
            ],
            "ai4bharat": [
                ("ai4bharat-en", "ai4bharat/indic-tts-coqui-misc-gpu--t4"),
                ("ai4bharat-kn", "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"),
            ]
        }

    def list_models(self):
        return self.models
    
    def model_enum(self, model_name: str) -> Tuple[str, str]:
        model_dict = {
            model[0]: (model_enum, model[1]) 
            for model_enum, models in self.models.items() 
            for model in models
        }
        return model_dict.get(model_name, (None, None))
    

    def speech(self, text: str) -> bytes:
        model_enum, model_name = self.model_enum(self.model)
        if model_enum == "coqui":
            return CoquiTTS(model_name, language=self.language).speech(text)
        elif model_enum == "ai4bharat":
            return Ai4BharatTTS(model_name, language=self.language).speech(text)
        else:
            return None
        