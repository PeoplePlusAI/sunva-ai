from groq import Groq
from TTS.api import TTS
from faster_whisper import WhisperModel
import os

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

def speech_to_text_groq(audio_chunk: str, client: Groq) -> str:
    transcription = client.audio.transcriptions.create(
        file=(audio_chunk, 
              open(audio_chunk, "rb").read()),
        model="whisper-large-v3",
        language="en",
        prompt=""
    )
    return transcription.text


model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8",
    cpu_threads=int(os.cpu_count() / 2),
)

def speech_to_text(audio_chunk, model):
    segments, info = model.transcribe(
        audio_chunk, beam_size=5
    )
    speech_text = " ".join(
        [
            segment.text for segment in segments
        ]
    )
    return speech_text 

def text_to_speech(text: str, tts: TTS=tts) -> list:
    audio = tts.tts(text)
    return audio