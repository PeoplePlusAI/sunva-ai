from core.utils.speech_utils import save_audio_to_file
from groq import AsyncGroq
from dotenv import load_dotenv
import os
import io

load_dotenv(
    dotenv_path="ops/.env"
)

groq_api_key = os.getenv("GROQ_API_KEY")

class GroqSTT:
    def __init__(self, model: str = "whisper-large-v3", language: str = "en"):
        self.client = AsyncGroq(
            api_key=groq_api_key
        )
        self.model = model
        self.language = language

    async def transcribe_stream(self, audio_buffer: io.BytesIO) -> str:
        transcription = ""
        while True:

            audio_file_name = save_audio_to_file(audio_buffer)

            partial_transcription = await self.client.audio.transcriptions.create(
                file=(
                    audio_file_name,
                    open(audio_file_name, "rb").read()),
                model=self.model,
                language=self.language,
                prompt=""
            )

            # Cleanup the audio file
            os.remove(audio_file_name)

            transcription += partial_transcription.text + " "
            
            # Yield the partial transcription
            yield partial_transcription.text

    async def transcribe(self, audio_file: str) -> str:
        with open(audio_file, "rb") as file:
            audio_buffer = io.BytesIO(file.read())
        
        full_transcription = ""
        async for partial_transcription in self.transcribe_stream(audio_buffer):
            full_transcription += partial_transcription

        return full_transcription.strip()