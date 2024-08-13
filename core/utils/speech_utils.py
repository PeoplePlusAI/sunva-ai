from concurrent.futures import ThreadPoolExecutor
import uuid
import numpy as np
import wave
import base64
import asyncio
import io
import os

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

def cleanup_audio_file(audio_filename: str):
    """Remove the temporary audio file."""
    os.remove(audio_filename)
