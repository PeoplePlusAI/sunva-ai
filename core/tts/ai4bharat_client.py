from core.utils.speech_utils import convert_audio_to_wav
from core.tts.bhashini_api import *
import json

class Ai4BharatTTS:
    def __init__(self, model_name: str, language: str):
        self.model_name = model_name
        self.language = language
        self.TTS = Bhashini()

    def speech(self, text: str) -> bytes:
        targetLanguage = self.language
        ttsServiceId = self.model_name
        text = text

        print(targetLanguage)
        print(ttsServiceId)
        print(text)

        response = self.TTS.textToSpeech(ttsServiceId,text,targetLanguage)
        print(response)
        #print(response.text)

        data = response
        
        # Extract the base64-encoded audio content
        # {'pipelineResponse': [{'taskType': 'tts', 'config': {'audioFormat': 'wav', 'language': {'sourceLanguage': 'en', 'sourceScriptCode': ''}, 'encoding': 'base64', 'samplingRate': 8000}, 'output': None, 'audio': [{'audioContent': 'UklGRpoCAQBXQVZFZm10IBIAAAADAAEAQB8AAAB9AAAEACAAAABmYWN0BAAAAJpAAABkYXRhaAIBAMT8CTqIEHc6SJRaOt4CZjq5CGU6yh1qOlJ5XDoFBWk65ENTOrF/WDoqZFQ64u9OOieTUToIOVc6ZIlOOjw3XTpe9VM64y5cOlGFWTrkbVY66qhaOpSFYzoXmkY6sN1KOmWSQDrlAE466HtGOmGCSzru3ko6LpRIOmCGVDorJls6KPVFOs
        audio_content = data['pipelineResponse'][0]['audio'][0]['audioContent']
                
        return audio_content