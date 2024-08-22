from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv(
    dotenv_path="ops/.env"
)

groq_api_key = os.getenv("GROQ_API_KEY")


class GroqSTT:
    def __init__(self, model: str = "whisper-large-v3", language: str = "en"):
        self.client = Groq(
            api_key=groq_api_key
        )
        self.model = model
        self.language = language

    def transcribe(self, audio_file: str) -> str:
        transcription = self.client.audio.transcriptions.create(
            file=(audio_file, 
                  open(audio_file, "rb").read()),
            model=self.model,
            language=self.language,
            prompt=""
        )
        return transcription.text