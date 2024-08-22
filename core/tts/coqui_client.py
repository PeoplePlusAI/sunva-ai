from TTS.api import TTS
from core.utils.speech_utils import convert_audio_to_wav

class CoquiTTS:
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC", language: str="en"):
        self.tts = TTS(model_name=model_name)
        self.language = language

    def speech(self, text: str) -> bytes:
        audio = self.tts.tts(
            text
        )
        if audio is not None:
            wav_data = convert_audio_to_wav(audio)
        else:
            wav_data = None
        return wav_data