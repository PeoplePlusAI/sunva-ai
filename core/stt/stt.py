from io import BytesIO
from typing import Tuple, Union
from core.stt.groq_client import GroqSTT
from core.stt.bodhi_client import BodhiSTT
from core.stt.malayalam_client import MalayalamSTT

class STT:
    def __init__(self, language: str):
        self.language = language
        self.models = {
            "GROQ": {
                "en": "whisper-large-v3",  # Default model for English
            },
            "BODHI": {
                "hi": "hi-general-v2-8khz",  # Default model for Hindi in Bodhi
                "kn": "kn-general-v2-8khz",  # Default model for Kannada
                # Add other languages and corresponding models
            },
            "MALAYALAM": {
                "ml": "Bajiyo/w2v-bert-2.0-nonstudio_and_studioRecords_final",  # Default model for Malayalam
            },
        }
        self.model_id, self.model_enum = self._select_model()

    def _select_model(self) -> Tuple[str, str]:
        for model_enum, lang_models in self.models.items():
            if self.language in lang_models:
                return lang_models[self.language], model_enum
        raise ValueError(f"Unsupported language: {self.language}")

    def list_models(self):
        return self.models

    async def transcribe_stream(self, audio_buffer: Union[str, BytesIO]):
        if self.model_enum == "GROQ":
            groq_stt = GroqSTT(self.model_id, language=self.language)
            async for partial_transcription in groq_stt.transcribe_stream(audio_buffer):
                yield partial_transcription
        elif self.model_enum == "BODHI":
            bodhi_stt = BodhiSTT(self.model_id, language=self.language)
            async for partial_transcription in bodhi_stt.transcribe_stream(audio_buffer):
                yield partial_transcription
        elif self.model_enum == "MALAYALAM":
            malayalam_stt = MalayalamSTT(self.model_id, language=self.language)
            async for partial_transcription in malayalam_stt.transcribe_stream(audio_buffer):
                yield partial_transcription
        else:
            raise ValueError(f"Unsupported language: {self.language}")