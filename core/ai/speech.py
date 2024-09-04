from core.stt.stt import STT
from core.tts.tts import TTS
import io

async def speech_to_text(audio_buffer: io.BytesIO, language: str):
    stt = STT(language=language)
    async for partial_transcription in stt.transcribe_stream(audio_buffer):
        yield partial_transcription

def text_to_speech(text: str, base_model: str, language: str) -> bytes:
    if base_model.startswith("ai4bharat"):
        base_model = base_model + "-" + language
    return TTS(model_name=base_model, language=language).speech(text)
