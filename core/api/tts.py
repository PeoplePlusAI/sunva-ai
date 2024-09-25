from fastapi import ( 
    WebSocket, 
    WebSocketDisconnect,
    APIRouter,
    Depends
)
from core.models.tts import TTSResponse
from core.ai.speech import text_to_speech
from core.utils.speech_utils import encode_wav_to_base64
from core.utils.executor_utils import executor
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.database import get_session
from core.models.db import SpeechDB
from core.db.redis_client import redis_client
from dotenv import load_dotenv
import asyncio
import base64
import pickle
import json
import os

# Initialize environment variables
load_dotenv(
    dotenv_path="ops/.env"
)

tts_model = os.getenv("TTS_BASE_MODEL", "coqui-tacotron2")
              
router = APIRouter()

@router.websocket("/v1/ws/speech")
async def tts_websocket(
    websocket: WebSocket, 
    session: AsyncSession = Depends(get_session)
):
    await websocket.accept()

    try:
        user_id = websocket.client.host
        cache_key = f"tts_session:{user_id}"
        await redis_client.delete(cache_key)  # Clear any existing data for this session
        
        while True:
            message = await websocket.receive_text()
            print(f"Received message: {message}")
            message = json.loads(message)
            
            selected_language = message.get("language", "en") #This sets the lang everywhere for pipeline.
            user_id = message.get("user_id", "default_user")

            if "text" in message:
                text = message["text"]
                print(f"Received text for TTS: {text}")

                wav_data = await asyncio.get_event_loop().run_in_executor(
                    executor, text_to_speech, text, tts_model, selected_language
                )
            else:
                wav_data = None
            print("tts_mdoel: ", tts_model)
            if wav_data and tts_model.startswith("ai4bharat"):
                # Cache in Redis
                print(wav_data)
                await redis_client.rpush(cache_key, json.dumps({"text": text, "wav_data": wav_data}))
                
                response = TTSResponse(audio=wav_data)
                await websocket.send_json(response.model_dump())
            elif wav_data and (tts_model == "coqui-glow-tts" or tts_model == "coqui-tacotron2"):
                wav_data_pickled = pickle.dumps(wav_data)
                audio_base64 = encode_wav_to_base64(wav_data)
                wav_data_base64 = base64.b64encode(wav_data_pickled).decode('utf-8')
                
                # Cache in Redis
                await redis_client.rpush(cache_key, json.dumps({"text": text, "wav_data": wav_data_base64}))
                
                response = TTSResponse(audio=audio_base64)
                await websocket.send_json(response.model_dump())
            else:
                print("No audio data received from text_to_speech")
                return {}
    except WebSocketDisconnect:
        print("TTS client disconnected")
    finally:
        # Persist cached data to DB at the end of the session
        cached_data = await redis_client.lrange(cache_key, 0, -1)
        for item in cached_data:
            # Each item is a JSON string; first, deserialize it into a dictionary
            item_dict = json.loads(item)
    
            # Now extract 'text' and 'wav_data' from the dictionary
            text = item_dict["text"]
            wav_data_base64 = item_dict["wav_data"]

            # Decode the base64 string back to bytes
            wav_data_bytes = base64.b64decode(wav_data_base64)

            # Convert the bytes back to the original list of floats
            wav_data = pickle.loads(wav_data_bytes)
            speech_record = SpeechDB(user_id=user_id, audio=wav_data, text=text, language=selected_language)
            session.add(speech_record)
        await session.commit()

        # Clear the cache for the session
        await redis_client.delete(cache_key)
