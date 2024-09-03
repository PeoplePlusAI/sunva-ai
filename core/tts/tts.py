from core.tts.coqui_client import CoquiTTS
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
            # Assuming CoquiTTS is a class from the Coqui library that loads the TTS model
            # Replace CoquiTTS with the actual class or function used to load your model
            print(f"Loading model: {model_name}")
            return CoquiTTS(model_name, language=self.language)
        else:
            # Raise an exception if the model is not found
            raise ValueError(f"Model {self.model} not found in the available models")

    def speech(self, text: str) -> bytes:
        if self.loaded_model:
            # Generate speech using the pre-loaded model
            return self.loaded_model.speech(text)
        else:
            return None