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
        self.accumulated_transcription = ""
        self.silent_count = 0
        self.new_words_count = 0
        self.total_words = 0
        self.SILENT_THRESHOLD = 5
        self.NEW_WORDS_THRESHOLD = 5  # Number of new words considered to be silence
        self.THANK_YOU_THRESHOLD = 3  # Number of repeated "thank you" to be considered as silence

    def detect_repeated_thank_you(self, transcription: str) -> bool:
        """
        Detects repeated occurrences of 'thank you' in the transcription.
        Returns True if 'thank you' is repeated more than the threshold times, indicating silence.
        """
        thank_you_count = transcription.lower().count("thank you")
        return thank_you_count >= self.THANK_YOU_THRESHOLD

    def process_transcription(self, transcription: str) -> str:
        """
        Processes the transcription to detect silence based on repeated 'thank you' 
        and tracks new words. Returns <EOF> if silence is detected.
        """
        # Count the number of new words
        words = transcription.split()
        new_words = len(words)
        self.new_words_count += new_words
        self.total_words += new_words

        # Accumulate the current transcription
        self.accumulated_transcription += transcription + " "

        # Check for repeated 'thank you' indicating silence
        if self.detect_repeated_thank_you(self.accumulated_transcription):
            self.silent_count += 1
        else:
            self.silent_count = 0

        # If silence threshold is reached due to "thank you" or low new words, return <EOF>
        if self.silent_count >= self.SILENT_THRESHOLD or self.new_words_count <= self.NEW_WORDS_THRESHOLD:
            self.accumulated_transcription = ""  # Reset after detecting silence
            self.new_words_count = 0  # Reset new words count
            return "<EOF>"

        return self.accumulated_transcription.strip()

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
        
            # Post-process the transcription
            result = self.process_transcription(partial_transcription.text)
            
            # If <EOF> is detected, return it as a signal to end processing
            if result == "<EOF>":
                yield "<EOF>"
            else:
                # Yield the processed transcription
                yield result
        finally:
            # Cleanup the audio file after processing
            os.remove(audio_file_name)

    async def transcribe(self, audio_file: str) -> str:
        with open(audio_file, "rb") as file:
            audio_buffer = io.BytesIO(file.read())

        full_transcription = ""
        async for partial_transcription in self.transcribe_stream(audio_buffer):
            if partial_transcription == "<EOF>":
                break
            full_transcription += partial_transcription

        return full_transcription.strip()