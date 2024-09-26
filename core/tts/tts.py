from core.tts.coqui_client import CoquiTTS
from core.tts.ai4bharat_client import Ai4BharatTTS

from typing import Tuple

class TTS:
    def __init__(self, model_name: str, language: str):
        self.model = model_name
        self.language = language
        self.models = {
            "ai4bharat": [
                ("ai4bharat-en", "ai4bharat/indic-tts-coqui-misc-gpu--t4"),
                ("ai4bharat-kn", "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"),
                ("ai4bharat-ml", "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"),
                ("ai4bharat-hi", "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4")
            ],
            "coqui": [
                ("coqui-tacotron2", "tts_models/en/ljspeech/tacotron2-DDC"),
                ("coqui-glow-tts", "tts_models/en/ljspeech/glow-tts"),
                ("coqui-waveglow", "tts_models/en/ljspeech/waveglow"),
            ]
        }
        self.loaded_model = self._load_model()

    def list_models(self):
        return self.models
    
    def model_enum(self, model_name: str) -> Tuple[str, str]:
        model_dict = {
            model[0]: (model_enum, model[1]) 
            for model_enum, models in self.models.items() 
            for model in models
        }
        return model_dict.get(model_name, (None, None))

    def _load_model(self):
        # Retrieve the model enum and model name from the models dictionary
        model_enum, model_name = self.model_enum(self.model)
        
        if model_enum == "coqui":
            print(f"Loading model: {model_name}")
            return CoquiTTS(model_name, language=self.language)
        elif model_enum == "ai4bharat":
            return Ai4BharatTTS(model_name, language=self.language)
        else:
            # Raise an exception if the model is not found
            raise ValueError(f"Model {self.model} not found in the available models")

    def speech(self, text: str) -> bytes:
        if self.loaded_model:
            # Generate speech using the pre-loaded model
            return self.loaded_model.speech(text)
        else:
            return None