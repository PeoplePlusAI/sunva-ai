import os
from dotenv import load_dotenv
from fastapi import (
    WebSocket, 
    WebSocketDisconnect, 
    HTTPException,
    APIRouter
)
from core.models.stt import (
    TranscriptionResponse,
    SingleTranscriptionResponse,
    Transcription,
    WebSocketResponse
)
from core.utils.speech_utils import (
    decode_audio_data,
    save_audio_to_file,
    cleanup_audio_file
)
from core.utils.executor_utils import executor
from core.ai.speech import speech_to_text_groq
from core.ai.text import process_transcription
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

router = APIRouter()

# In-memory storage for transcriptions and processed text (for demonstration purposes)
transcriptions = []
processed_texts = []

@router.get("/transcriptions", response_model=TranscriptionResponse)
async def get_transcriptions():
    return {"transcriptions": [Transcription(id=i, transcription=t) for i, t in enumerate(transcriptions)]}


@router.get("/transcriptions/{transcription_id}", response_model=SingleTranscriptionResponse)
async def get_transcription(transcription_id: int):
    if transcription_id < 0 or transcription_id >= len(transcriptions):
        raise HTTPException(status_code=404, detail="Transcription not found")
    return {"transcription": Transcription(id=transcription_id, transcription=transcriptions[transcription_id])}


@router.websocket("/v1/ws/transcription")
async def websocket_transcribe_and_process(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = io.BytesIO()  # Buffer to store continuous audio stream
    transcription = ""
    word_count = 0
    WORD_THRESHOLD = 30
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if "audio" in message:
                audio_data = decode_audio_data(message)
                audio_buffer.write(audio_data)

                # Save the buffer as a temporary WAV file
                audio_filename = save_audio_to_file(audio_buffer)

                # Perform transcription on the continuous audio stream
                partial_transcription = await asyncio.get_event_loop().run_in_executor(
                    executor, speech_to_text_groq, audio_filename, client
                )
                
                audio_buffer.seek(0)  # Reset buffer for next chunk
                cleanup_audio_file(audio_filename)  # Clean up the temporary file
                
                # Accumulate the transcription and count words
                transcription += partial_transcription + " "
                word_count += len(partial_transcription.split())
                
                # Send the real-time transcription back to the client
                response = WebSocketResponse(transcription=partial_transcription)
                await websocket.send_text(response.model_dump_json())
                
                # If the word count exceeds the threshold, process the transcription
                if word_count >= WORD_THRESHOLD:
                    processed_text = await asyncio.get_event_loop().run_in_executor(
                        executor, process_transcription, transcription.strip(), client)
                    
                    # Send the processed text back to the client
                    response = WebSocketResponse(transcription=transcription.strip(), processed_text=processed_text)
                    await websocket.send_text(response.model_dump_json())
                    
                    # Reset the transcription and word count
                    transcription = ""
                    word_count = 0
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        traceback.print_exc()