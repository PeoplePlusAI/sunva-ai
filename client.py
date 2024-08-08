import asyncio
import websockets
import pyaudio
import json
import base64
import time

# Constants
TRANSCRIBE_WS_URL = "ws://localhost:8000/transcribe"
PROCESS_WS_URL = "ws://localhost:8000/process"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
TRANSCRIBE_SECONDS = 5  # Transcribe every 5 seconds of audio
SILENCE_THRESHOLD = 500  # Adjust this threshold as needed
SENTENCE_THRESHOLD = 3  # Trigger process after 3 sentences
WORD_THRESHOLD = 50  # Trigger process after 50 words

# Globals
transcription = ""
last_transcription_time = 0
audio_queue = asyncio.Queue()

def is_silent(data):
    # This is a simplified is_silent function
    # We should improve it later
    return False

def count_sentences(text):
    return text.count('. ')

def count_words(text):
    return len(text.split())
    

def is_threshold_reached(text):
    if count_words(text) >= WORD_THRESHOLD:
        return True


async def transcribe():
    global transcription
    print("Transcription coroutine started")
    try:
        async with websockets.connect(TRANSCRIBE_WS_URL) as websocket:
            print("Connected to transcription WebSocket")
            print("Transcription: ")
            while True:
                audio_chunks = []
                for _ in range(0, int(RATE / CHUNK * TRANSCRIBE_SECONDS)):
                    audio_chunk = await audio_queue.get()
                    #print(f"Read audio chunk: {len(audio_chunk)} bytes")
                    #if is_silent(audio_chunk):
                    #    print("Silent audio chunk, skipping")
                    #    continue
                    audio_chunks.append(audio_chunk)
                
                # Combine audio chunks into one audio segment
                audio_data = b''.join(audio_chunks)
                #print("Combined audio data size:", len(audio_data))
                
                # Encode the combined audio segment to base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                await websocket.send(json.dumps({"audio": audio_base64}))
                
                #print("Sent audio segment to WebSocket")
                response = await websocket.recv()
                #print("Received response from WebSocket")
                response_data = json.loads(response)
                if "transcription" in response_data:
                    transcription += response_data["transcription"] + " "
                    #print("Transcription: ", transcription)
                    print(response_data["transcription"] + " ", end="", flush=True)
                    global last_transcription_time
                    last_transcription_time = time.time()  # Update the last transcription time
    except Exception as e:
        print(f"Transcription error: {e}")

async def process():
    global transcription
    print("Process coroutine started")
    try:
        async with websockets.connect(PROCESS_WS_URL) as websocket:
            print("Connected to processing WebSocket")
            while True:
                if transcription and is_threshold_reached(transcription):
                    await websocket.send(json.dumps({"text": transcription}))
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    if "processed_text" in response_data:
                        print("\nProcessed Text: ", response_data["processed_text"])
                        transcription = ""  # Reset the transcription
                await asyncio.sleep(1)  # Check every second
    except Exception as e:
        print(f"Processing error: {e}")

async def audio_stream():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")
    try:
        while True:
            audio_chunk = stream.read(CHUNK, exception_on_overflow=False)
            await audio_queue.put(audio_chunk)
            #print("Audio chunk put in queue")  # Debug statement
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        print("Audio stream cancelled.")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("Audio stream closed.")

async def main():
    transcribe_task = asyncio.create_task(transcribe())
    process_task = asyncio.create_task(process())
    audio_task = asyncio.create_task(audio_stream())

    try:
        await asyncio.gather(transcribe_task, process_task, audio_task)
    except KeyboardInterrupt:
        transcribe_task.cancel()
        process_task.cancel()
        audio_task.cancel()
        await asyncio.gather(transcribe_task, process_task, audio_task, return_exceptions=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Exception in main: {e}")