from fastapi import (
    FastAPI, 
    WebSocket, 
    WebSocketDisconnect, 
    HTTPException
)
from core.ai.speech import (
    speech_to_text_groq, 
    text_to_speech
)
from fastapi.responses import FileResponse
from core.ai.text import process_transcription
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from groq import Groq
import traceback
import numpy as np
import asyncio
import base64
import uuid
import wave
import json
import io
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

def float32_to_int16(audio_array):
    # Scale float32 array to int16
    return np.int16(audio_array * 32767)

import io


@app.websocket("/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = io.BytesIO()  # Buffer to store continuous audio stream
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if "audio" in message:
                audio_base64 = message["audio"]
                audio_data = base64.b64decode(audio_base64)
                audio_buffer.write(audio_data)

                # Save the buffer as a temporary WAV file
                audio_filename = f"temp_{uuid.uuid4().hex}.wav"
                with wave.open(audio_filename, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(16000)
                    wf.writeframes(audio_buffer.getvalue())

                # Perform transcription on the continuous audio stream
                partial_transcription = await asyncio.get_event_loop().run_in_executor(
                    executor, speech_to_text_groq, audio_filename, client)
                
                audio_buffer.seek(0)  # Reset buffer for next chunk
                print("Partial transcription:", partial_transcription)
                os.remove(audio_filename)  # Clean up the temporary file
                
                # Send the real-time transcription back to the client
                await websocket.send_text(json.dumps({"transcription": partial_transcription}))
                print("Sent transcription:", partial_transcription)
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        traceback.print_exc()


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
                
                # Simulate progressive processing (for demonstration)
                partial_texts = text_to_process.split(". ")
                for part in partial_texts:
                    processed_text = await asyncio.get_event_loop().run_in_executor(
                        executor, process_transcription, part, client)
                    if processed_text:
                        processed_texts.append(processed_text)
                        await websocket.send_text(json.dumps({"processed_text": processed_text}))
                        print("Sent processed text:", processed_text)
                        await asyncio.sleep(0.5)  # Simulate delay for each part
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


@app.websocket("/tts")
async def tts_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            print(f"Received text for TTS: {text}")
            audio_data = await asyncio.get_event_loop().run_in_executor(
                executor, text_to_speech, text)
            if audio_data:
                # Convert float32 numpy array to int16
                audio_int16 = float32_to_int16(np.array(audio_data, dtype=np.float32))
                audio_bytes = audio_int16.tobytes()
                
                # Create a WAV file in memory
                wav_io = io.BytesIO()
                with wave.open(wav_io, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)  # 2 bytes per sample
                    wav_file.setframerate(16000)
                    wav_file.writeframes(audio_bytes)
                
                wav_io.seek(0)
                # Encode the WAV file to base64
                audio_base64 = base64.b64encode(wav_io.read()).decode('utf-8')
                
                await websocket.send_json({"audio": audio_base64})
            else:
                print("No audio data received from text_to_speech")
    except WebSocketDisconnect:
        print("TTS client disconnected")

@app.get("/")
async def get():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)