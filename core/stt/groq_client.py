import os
import io
from dotenv import load_dotenv
from groq import AsyncGroq
from core.utils.speech_utils import save_audio_to_file

load_dotenv(dotenv_path="ops/.env")
groq_api_key = os.getenv("GROQ_API_KEY")

class GroqSTT:
    def __init__(self, model: str = "whisper-large-v3", language: str = "en"):
        self.client = AsyncGroq(api_key=groq_api_key)
        self.model = model
        self.language = language

    async def transcribe_stream(self, audio_buffer: io.BytesIO) -> str:

        # Reset buffer to the start position
        audio_buffer.seek(0)

        # Save audio buffer to a temporary file
        audio_file_name = save_audio_to_file(audio_buffer)

        try:
            partial_transcription = await self.client.audio.transcriptions.create(
                file=(audio_file_name, open(audio_file_name, "rb").read()),
                model=self.model,
                language=self.language,
                prompt=""
            )
        

            # Yield the transcription
            yield partial_transcription.text
        finally:
            # Cleanup the audio file after processing
            os.remove(audio_file_name)

    async def transcribe(self, audio_file: str) -> str:
        with open(audio_file, "rb") as file:
            audio_buffer = io.BytesIO(file.read())

        full_transcription = ""
        async for partial_transcription in self.transcribe_stream(audio_buffer):
            full_transcription += partial_transcription

        return full_transcription.strip()