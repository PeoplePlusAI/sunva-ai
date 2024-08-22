from core.stt.stt import STT
from core.tts.tts import TTS

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

def speech_to_text(audio_file: str, base_model: str, language: str) -> str:
    return STT(base_model, language=language).transcribe(audio_file)

def text_to_speech(text: str, base_model: str, language: str) -> bytes:
    return TTS(model_name=base_model, language=language).speech(text)