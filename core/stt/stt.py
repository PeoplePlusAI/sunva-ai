import asyncio
from io import BytesIO
from typing import Tuple, Union
from core.stt.groq_client import GroqSTT
from core.stt.bodhi_client import BodhiSTT  # Assume you've saved the BodhiSTT class in this file

class STT:
    def __init__(self, model_id: str = "Whisper Large", language: str = "en"):
        self.model_id = model_id
        self.models = {
            "GROQ": [
                ("Whisper Large", "whisper-large-v3"),
                ("Whisper Medium", "whisper-medium-v3"),
                ("Whisper Small", "whisper-small-v3"),
            ],
            "BODHI": [
                ("Hindi General", "hi-general-v2-8khz"),
                ("Kannada General", "kn-general-v2-8khz"),
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


    async def transcribe_stream(self, audio_buffer: Union[str, BytesIO]):
        model_enum, model_id = self.model_enum(self.model_id)
        if model_enum == "GROQ":
            groq_stt = GroqSTT(model_id, language=self.language)
            async for partial_transcription in groq_stt.transcribe_stream(audio_buffer):
                yield partial_transcription
        elif model_enum == "BODHI":
            bodhi_stt = BodhiSTT(model_id, language=self.language)
            async for partial_transcription in bodhi_stt.transcribe_stream(audio_buffer):
                yield partial_transcription
        else:
            raise ValueError(f"Unsupported model: {self.model_id}")