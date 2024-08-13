from fastapi import ( 
    WebSocket, 
    WebSocketDisconnect,
    APIRouter
)
from core.models.tts import TTSResponse
from core.ai.speech import text_to_speech
from core.utils.speech_utils import (
    convert_audio_to_wav,
    encode_wav_to_base64
)
from core.utils.executor_utils import executor
from dotenv import load_dotenv
from groq import Groq
import asyncio
import os

# Initialize environment variables
load_dotenv(
    dotenv_path="ops/.env"
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
              
router = APIRouter()


@router.websocket("/v1/ws/speech")
async def tts_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            print(f"Received text for TTS: {text}")

            audio_data = await asyncio.get_event_loop().run_in_executor(
                executor, text_to_speech, text
            )
    
            if audio_data is not None:
                wav_data = convert_audio_to_wav(audio_data)
                audio_base64 = encode_wav_to_base64(wav_data)
                response = TTSResponse(audio=audio_base64)
                await websocket.send_json(response.model_dump())
            else:
                audio_base64 = None
                print("No audio data received from text_to_speech")
                return {}
    except WebSocketDisconnect:
        print("TTS client disconnected")
