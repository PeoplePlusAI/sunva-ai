from fastapi import (
    FastAPI, 
    WebSocket, 
    WebSocketDisconnect, 
    HTTPException
)
from core.ai.speech import speech_to_text_groq
from core.ai.text import process_transcription
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from groq import Groq
import asyncio
import base64
import uuid
import wave
import json
import os

# Initialize environment variables
load_dotenv(
    dotenv_path="ops/.env"
)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


app = FastAPI()

# In-memory storage for transcriptions and processed text (for demonstration purposes)
transcriptions = []
processed_texts = []

executor = ThreadPoolExecutor(max_workers=4)

@app.websocket("/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    transcription = ""
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            print("Received message:", message)
            if "audio" in message:
                audio_base64 = message["audio"]
                # Decode the base64 audio data
                audio_data = base64.b64decode(audio_base64)
                print("Received audio data of length:", len(audio_data))
                # Save the decoded audio data to a temporary WAV file
                audio_filename = f"temp_{uuid.uuid4().hex}.wav"
                with wave.open(audio_filename, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # Assuming 16-bit PCM format
                    wf.setframerate(16000)
                    wf.writeframes(audio_data)
                
                # Perform transcription on the audio file
                partial_transcription = await asyncio.get_event_loop().run_in_executor(
                    executor, speech_to_text_groq, audio_filename, client)
                print("Partial transcription:", partial_transcription)
                os.remove(audio_filename)  # Clean up the temporary file
                
                # Only add new transcriptions to avoid repetition
                transcription += partial_transcription + " "
                transcriptions.append(partial_transcription)
                # Send the real-time transcription back to the client
                await websocket.send_text(json.dumps({"transcription": partial_transcription}))
                print("Sent transcription:", partial_transcription)
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")


@app.websocket("/process")
async def websocket_process(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if "text" in message:
                text_to_process = message["text"]
                print("Received text for processing:", text_to_process)
                # Process the received text
                processed_text = await asyncio.get_event_loop().run_in_executor(
                    executor, process_transcription, text_to_process, client)
                processed_texts.append(processed_text)
                # Send the processed text back to the client
                await websocket.send_text(json.dumps({"processed_text": processed_text}))
                print("Sent processed text:", processed_text)
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

@app.get("/transcriptions")
async def get_transcriptions():
    return transcriptions

@app.get("/transcriptions/{transcription_id}")
async def get_transcription(transcription_id: int):
    if transcription_id < 0 or transcription_id >= len(transcriptions):
        raise HTTPException(status_code=404, detail="Transcription not found")
    return transcriptions[transcription_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)