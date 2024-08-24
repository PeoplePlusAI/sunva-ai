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
from core.ai.speech import speech_to_text
from core.ai.text import process_transcription
from core.db.redis_client import redis_client
import traceback
import asyncio
import json
import io
import os

load_dotenv(
    dotenv_path="ops/.env"
)

speech_base_model = os.getenv("SPEECH_BASE_MODEL", "Whisper Large")

llm_base_model = os.getenv("BASE_MODEL", "GPT-4o")

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
async def websocket_transcribe_and_process(websocket: WebSocket):
    await websocket.accept()
    user_id = websocket.client.host

    full_transcription = ""
    processing_candidate = ""
    processed_transcription = ""
    word_count = 0
    audio_buffer = io.BytesIO()
    WORD_THRESHOLD = 30

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            language = message.get("language", "en")
            
            if "audio" in message:
                audio_data = decode_audio_data(message)
                audio_buffer.write(audio_data)

                # Reset buffer position to the beginning
                audio_buffer.seek(0)

                async for partial_transcription in speech_to_text(audio_buffer, speech_base_model, language):
                    # Check for <EOF> signal
                    if partial_transcription == "<EOF>":
                        # Process the current candidate if EOF is detected
                        if processing_candidate.strip():
                            partial_processed_transcription = await asyncio.get_event_loop().run_in_executor(
                                executor, process_transcription, processing_candidate.strip(), llm_base_model
                            )
                            if partial_processed_transcription:
                                processed_transcription += partial_processed_transcription.get("processed_text") + " "
                                processing_candidate = ""
                                word_count = 0

                                await redis_client.hset(f"transcription:{user_id}", mapping={
                                    "transcription": full_transcription.strip(),
                                    "processed_transcription": processed_transcription.strip()
                                })

                                response = WebSocketResponse(
                                    processed_text=partial_processed_transcription.get("processed_text").strip(),
                                    original_text=partial_processed_transcription.get("original_text").strip(),
                                    style=partial_processed_transcription.get("style")
                                )
                                await websocket.send_text(response.model_dump_json())
                        continue  # Skip the loop if EOF is detected

                    full_transcription += partial_transcription + " "
                    processing_candidate += partial_transcription + " "
                    word_count += len(partial_transcription.split())

                    response = WebSocketResponse(transcription=partial_transcription)
                    await websocket.send_text(response.model_dump_json())

                    if word_count >= WORD_THRESHOLD:
                        partial_processed_transcription = await asyncio.get_event_loop().run_in_executor(
                            executor, process_transcription, processing_candidate.strip(), llm_base_model
                        )
                        if partial_processed_transcription:
                            processed_transcription += partial_processed_transcription.get("processed_text") + " "
                            processing_candidate = ""
                            word_count = 0

                            await redis_client.hset(f"transcription:{user_id}", mapping={
                                "transcription": full_transcription.strip(),
                                "processed_transcription": processed_transcription.strip()
                            })

                            response = WebSocketResponse(
                                processed_text=partial_processed_transcription.get("processed_text").strip(),
                                original_text=partial_processed_transcription.get("original_text").strip(),
                                style=partial_processed_transcription.get("style")
                            )
                            print(response.model_dump_json())
                            await websocket.send_text(response.model_dump_json())

                # Clear the buffer for the next chunk
                audio_buffer = io.BytesIO()

    except WebSocketDisconnect:
        print(f"Client {user_id} disconnected")

        # Process any remaining transcription
        if processing_candidate.strip():
            partial_processed_transcription = await asyncio.get_event_loop().run_in_executor(
                executor, process_transcription, processing_candidate.strip(), llm_base_model
            )
            processed_transcription += partial_processed_transcription.get("processed_text") + " "

        await redis_client.hset(f"transcription:{user_id}", mapping={
            "transcription": full_transcription.strip(),
            "processed_transcription": processed_transcription.strip()
        })

    except Exception as e:
        traceback.print_exc()

        # Process any remaining transcription in case of an exception
        if processing_candidate.strip():
            partial_processed_transcription = await asyncio.get_event_loop().run_in_executor(
                executor, process_transcription, processing_candidate.strip(), llm_base_model
            )
            processed_transcription += partial_processed_transcription.get("processed_text") + " "

        await redis_client.hset(f"transcription:{user_id}", mapping={
            "transcription": full_transcription.strip(),
            "processed_transcription": processed_transcription.strip()
        })

    finally:
        # Final processing before closing
        if processing_candidate.strip():
            partial_processed_transcription = await asyncio.get_event_loop().run_in_executor(
                executor, process_transcription, processing_candidate.strip(), llm_base_model
            )
            processed_transcription += partial_processed_transcription.get("processed_text") + " "

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