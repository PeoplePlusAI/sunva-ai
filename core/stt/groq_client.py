import os
import io
import numpy as np
import librosa
import traceback
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
        self.new_words_count = 0
        self.total_words = 0
        self.previous_word_count = 0  # Track the word count from the previous transcription

    async def transcribe_stream(self, audio_buffer: io.BytesIO) -> str:

        # Reset buffer to the start position
        audio_buffer.seek(0)

        # Save audio buffer to a temporary file
        audio_file_name = save_audio_to_file(audio_buffer)

        # Preprocess the audio file to check if it is mostly silent
        if self.preprocess_audio(audio_file_name):
            yield "<EOF>"
            return

        try:
            partial_transcription = await self.client.audio.transcriptions.create(
                file=(audio_file_name, open(audio_file_name, "rb").read()),
                model=self.model,
                language=self.language,
                prompt=""
            )
        
            yield partial_transcription.text
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
    
    def preprocess_audio(self, audio_file_name: str) -> bool:
        # Load audio data from the file
        audio_data, sample_rate = librosa.load(audio_file_name, sr=None, mono=True)

        # Debugging: Check the type and shape of the loaded audio data
        if not isinstance(audio_data, np.ndarray):
            raise ValueError(f"Expected audio_data to be a numpy.ndarray, but got {type(audio_data)}")

        # Check if the audio is mostly silent
        return self.is_silent(audio_data, sample_rate)
    

    def is_silent(self, audio_data: np.ndarray, sample_rate: int, 
                                  energy_threshold: float = 0.02,
                                  silent_proportion_threshold: float = 0.75) -> bool:
    
        # Convert audio data to float32 if it's not already
        if audio_data.dtype != np.float32 and audio_data.dtype != np.float64:
            audio_data = audio_data.astype(np.float32)

        # Calculate STFT
        try:
            S = np.abs(librosa.stft(audio_data))
        except Exception as e:
            raise ValueError(f"STFT calculation failed: {e}")

        # Calculate the energy of each frame
        frame_energies = np.mean(S, axis=0)

        # Proportion of frames with energy below the threshold
        low_energy_frames = np.sum(frame_energies < energy_threshold)
        proportion_low_energy = low_energy_frames / len(frame_energies)

        # Determine if the audio is mostly silent based on the proportion of low-energy frames
        is_silent = proportion_low_energy >= silent_proportion_threshold

        return is_silent
