from concurrent.futures import ThreadPoolExecutor
import uuid
import numpy as np
import wave
import base64
import asyncio
import io
import os
import subprocess
import librosa

def float32_to_int16(audio_array):
    """Scale float32 array to int16."""
    return np.int16(audio_array * 32767)

def convert_audio_to_wav(audio_data: np.ndarray) -> bytes:
    """Convert float32 numpy array to int16 and create a WAV file in memory."""
    audio_int16 = float32_to_int16(np.array(audio_data, dtype=np.float32))
    audio_bytes = audio_int16.tobytes()
    
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(16000)
        wav_file.writeframes(audio_bytes)
    
    wav_io.seek(0)
    return wav_io.read()

def encode_wav_to_base64(wav_data: bytes) -> str:
    """Encode WAV file to base64."""
    return base64.b64encode(wav_data).decode('utf-8')

async def handle_tts_request(text: str, executor: ThreadPoolExecutor, tts_method) -> str:
    """Handle TTS request by synthesizing speech and returning base64 encoded audio."""
    audio_data = await asyncio.get_event_loop().run_in_executor(executor, tts_method, text)
    
    if audio_data is not None:
        wav_data = convert_audio_to_wav(audio_data)
        return encode_wav_to_base64(wav_data)
    
    return ""

def decode_audio_data(message: dict) -> bytes:
    """Decode the base64 audio data from the received message."""
    audio_base64 = message["audio"]
    return base64.b64decode(audio_base64)


def save_audio_to_file(audio_buffer: io.BytesIO) -> str:
    """Save the audio buffer to a temporary WAV file."""
    audio_filename = f"temp_{uuid.uuid4().hex}.wav"
    with wave.open(audio_filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_buffer.getvalue())
    return audio_filename

def save_audio_to_m4a_ffmpeg(audio_buffer: io.BytesIO) -> str:
    """Save the audio buffer to a temporary M4A file using FFmpeg."""
    audio_filename = f"temp_{uuid.uuid4().hex}.m4a"

    # Write the BytesIO buffer to a temporary WAV file
    with open("temp.wav", "wb") as temp_wav:
        temp_wav.write(audio_buffer.getvalue())

    # Use FFmpeg to convert the WAV file to M4A
    subprocess.run(["ffmpeg", "-i", "temp.wav", audio_filename, "-y"], check=True)

    # Optionally, remove the temporary WAV file
    if os.path.exists("temp_*.wav"):
        os.remove("temp.wav")


    return audio_filename

def cleanup_audio_file(audio_filename: str):
    """Remove the temporary audio file."""
    os.remove(audio_filename)

def generate_message_id() -> str:
    """
    Generates a unique message ID using UUID4.
    Returns:
        str: A unique message ID.
    """
    return str(uuid.uuid4())


def is_silent(audio_data: np.ndarray, energy_threshold: float = 0.02, silent_proportion_threshold: float = 0.75) -> bool:
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
    is_silent = proportion_low_energy >= silent_proportion_threshold or proportion_low_energy == 0.0
    return is_silent
