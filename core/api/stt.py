from dotenv import load_dotenv
from fastapi import (
    WebSocket, 
    WebSocketDisconnect, 
    HTTPException,
    APIRouter,
    Depends
)
from core.models.stt import (
    TranscriptionResponse,
    SingleTranscriptionResponse,
    WebSocketResponse
)
from core.utils.speech_utils import (
    decode_audio_data,
    save_audio_to_file,
    cleanup_audio_file
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from core.models.db import TranscriptionDB
from core.db.database import get_session
from core.utils.executor_utils import executor
from core.ai.speech import speech_to_text_groq
from core.ai.text import process_transcription
from core.db.redis_client import redis_client
from groq import Groq
import traceback
import asyncio
import json
import io
import os

load_dotenv(
    dotenv_path="ops/.env"
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

base_model = os.getenv("BASE_MODEL")

router = APIRouter()

user_sessions = {}

@router.get("/transcriptions", response_model=TranscriptionResponse)
async def get_transcriptions(session: AsyncSession = Depends(get_session)):
    transcriptions = await session.execute(select(TranscriptionDB))
    return {"transcriptions": transcriptions.scalars().all()}

# API endpoint to retrieve a specific transcription by ID
@router.get("/transcriptions/{transcription_id}", response_model=SingleTranscriptionResponse)
async def get_transcription(transcription_id: int, session: AsyncSession = Depends(get_session)):
    transcription = await session.get(TranscriptionDB, transcription_id)
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return {"transcription": transcription}


@router.websocket("/v1/ws/transcription")
async def websocket_transcribe_and_process(
    websocket: WebSocket
):
    await websocket.accept()
    user_id = websocket.client.host

    # Initialize transcription and word count for this session
    full_transcription = ""
    transcription = ""
    processed_transcription = ""
    word_count = 0
    audio_buffer = io.BytesIO()
    WORD_THRESHOLD = 30

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if "audio" in message:
                audio_data = decode_audio_data(message)
                audio_buffer.write(audio_data)

                audio_filename = save_audio_to_file(audio_buffer)

                partial_transcription = await asyncio.get_event_loop().run_in_executor(
                    executor, speech_to_text_groq, audio_filename, client
                )

                audio_buffer.seek(0)
                cleanup_audio_file(audio_filename)

                transcription += partial_transcription + " "
                full_transcription += partial_transcription + " "
                word_count += len(partial_transcription.split())

                response = WebSocketResponse(transcription=partial_transcription)
                await websocket.send_text(response.model_dump_json())

                if word_count >= WORD_THRESHOLD:
                    partial_processed_transcription = await asyncio.get_event_loop().run_in_executor(
                        executor, process_transcription, transcription.strip(), base_model
                    )

                    processed_transcription += partial_processed_transcription + " "
                    word_count = 0

                    # Store the transcription in Redis
                    await redis_client.hset(f"transcription:{user_id}", mapping={
                        "transcription": full_transcription.strip(),
                        "processed_transcription": processed_transcription.strip()
                    }) 

                    response = WebSocketResponse(
                        transcription=partial_transcription.strip(),
                        processed_text=partial_processed_transcription.strip()
                    )
                    await websocket.send_text(response.model_dump_json())

                    transcription = ""

    except WebSocketDisconnect:
        print(f"Client {user_id} disconnected")
        # Handle disconnection gracefully
        await redis_client.hset(f"transcription:{user_id}", mapping={
            "transcription": full_transcription.strip(),
            "processed_transcription": processed_transcription.strip()
        })
    except Exception as e:
        traceback.print_exc()
        # Handle errors
        await redis_client.hset(f"transcription:{user_id}", mapping={
            "transcription": full_transcription.strip(),
            "processed_transcription": processed_transcription.strip()
        })


@router.post("/v1/transcription/save")
async def save_transcription(user_id: str, session: AsyncSession = Depends(get_session)):
    # Retrieve the transcription data from Redis
    session_data = await redis_client.hgetall(f"transcription:{user_id}")

    if not session_data:
        raise HTTPException(status_code=404, detail="No active transcription session for this user.")

    # Convert Redis data from bytes to string
    transcription = session_data.get(b"transcription", b"").decode("utf-8")
    processed_transcription = session_data.get(b"processed_transcription", b"").decode("utf-8")

    if transcription or processed_transcription:
        new_entry = TranscriptionDB(
            user_id=user_id,
            transcription=transcription,
            processed_text=processed_transcription
        )
        session.add(new_entry)
        await session.commit()

        # Delete the session data from Redis after saving to the database
        await redis_client.delete(f"transcription:{user_id}")

        return {"status": "success", "message": "Transcription saved successfully."}
    else:
        raise HTTPException(status_code=500, detail="Failed to retrieve session data.")