import os
import io
import time
import numpy as np
import uuid
import traceback
from dotenv import load_dotenv
from groq import AsyncGroq
from pydub import AudioSegment
from core.utils.speech_utils import is_silent

load_dotenv(dotenv_path="ops/.env")
groq_api_key = os.getenv("GROQ_API_KEY")

class GroqSTT:
    def __init__(self, model: str = "whisper-large-v3", language: str = "en"):
        self.client = AsyncGroq(api_key=groq_api_key)
        self.model = model
        self.language = language
        self.accumulated_transcription = ""
        self.new_words_count = 0
        self.total_words = 0
        self.previous_word_count = 0  # Track the word count from the previous transcription

    async def transcribe_stream(self, audio_buffer: io.BytesIO) -> str:

        start_time = time.time()

        # Reset buffer to the start position
        audio_buffer.seek(0)

        # Preprocess the audio buffer to check if it is mostly silent
        if self.is_speech_silent(audio_buffer):
            yield "<EOF>"
            return
        
        # Reset the original buffer for transcription use
        audio_buffer.seek(0)

        audio_file_name = f"temp_{uuid.uuid4().hex}.m4a"
        
        try:
            partial_transcription = await self.client.audio.transcriptions.create(
                file=(audio_file_name, audio_buffer.read()),
                model=self.model,
                language=self.language,
                prompt=""
            )
            print(partial_transcription.text)
        
            yield partial_transcription.text
        except Exception as e:
            traceback.print_exc()

        end_time = time.time()

        print(f"Transcription time: {end_time - start_time:.4f} seconds")

    async def transcribe(self, audio_file: str) -> str:
        with open(audio_file, "rb") as file:
            audio_buffer = io.BytesIO(file.read())

        full_transcription = ""
        async for partial_transcription in self.transcribe_stream(audio_buffer):
            if partial_transcription == "<EOF>":
                break
            full_transcription += partial_transcription

        return full_transcription.strip()
    

    def is_speech_silent(self, audio_buffer: io.BytesIO) -> bool:
        # Convert the buffer to an AudioSegment
        audio_buffer.seek(0)
        audio_segment = AudioSegment.from_file(audio_buffer, format="wav")  # Handling as WAV format
        
        # Convert to numpy array
        audio_data = np.array(audio_segment.get_array_of_samples())

        # If the audio has more than one channel, convert to mono
        if audio_segment.channels > 1:
            audio_data = audio_data.reshape((-1, audio_segment.channels))
            audio_data = audio_data.mean(axis=1)

        # Normalize the audio data to the range -1 to 1
        audio_data = audio_data / np.iinfo(audio_data.dtype).max

        # Debugging: Check the type and shape of the loaded audio data
        if not isinstance(audio_data, np.ndarray):
            raise ValueError(f"Expected audio_data to be a numpy.ndarray, but got {type(audio_data)}")
        
        # Check if the audio is mostly silent
        return is_silent(audio_data)


    