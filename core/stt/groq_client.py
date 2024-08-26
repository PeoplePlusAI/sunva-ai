import os
import io
import numpy as np
import librosa
import uuid
from dotenv import load_dotenv
from groq import AsyncGroq
from core.utils.speech_utils import save_audio_to_m4a_ffmpeg

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
        # audio_file_name = save_audio_to_m4a_ffmpeg(audio_buffer)
        audio_file_name = f"temp_{uuid.uuid4().hex}.m4a"
        # Preprocess the audio file to check if it is mostly silent
        # if self.is_silent_scipy(audio_buffer):
        #     yield "<EOF>"
        #     return

        try:
            partial_transcription = await self.client.audio.transcriptions.create(
                file=(audio_file_name, audio_buffer.read()),
                model=self.model,
                language=self.language,
                prompt=""
            )
            print(partial_transcription.text)
        
            yield partial_transcription.text
        except:
            print("exception")
        # finally:
        #     # Cleanup the audio file after processing
        #     # os.remove(audio_file_name)
        #     print("finally")

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
        print(f"Audio data type: {type(audio_data)}, shape: {audio_data.shape}")

        # Check if the audio is mostly silent
        return self.is_silent(audio_data, sample_rate)

    def is_silent(self, audio_data: np.ndarray, 
                        energy_threshold: float = 0.02,
                        silent_proportion_threshold: float = 0.75) -> bool:
    
        # Convert audio data to float32 if it's not already
        if audio_data.dtype != np.float32 and audio_data.dtype != np.float64:
            audio_data = audio_data.astype(np.float32)
    
        print(f"Audio data type after conversion (if any): {audio_data.dtype}")

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

        # Debugging information
        print(f"Total frames: {len(frame_energies)}, Low-energy frames: {low_energy_frames}")
        print(f"Proportion of low-energy frames: {proportion_low_energy}")

        # Determine if the audio is mostly silent based on the proportion of low-energy frames
        is_silent = ""
        if (proportion_low_energy >= silent_proportion_threshold):
            is_silent = True
        elif (proportion_low_energy >= 0.20):
            is_silent = False
        elif (proportion_low_energy == 0.0):
            is_silent = True
        print(f"Is Mostly Silent: {is_silent}")

        return is_silent