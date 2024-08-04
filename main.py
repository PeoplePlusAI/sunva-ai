import os
import asyncio
import pyaudio
import wave
from queue import Queue
from core.ai.speech import speech_to_text_groq
from core.ai.text import process_transcription
from dotenv import load_dotenv
import streamlit as st
from groq import Groq
import traceback
import time

# Initialize environment variables
load_dotenv(
    dotenv_path="ops/.env"
)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize PyAudio and queue
audio_queue = Queue()
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

transcriptions = []
proccesed_candidates = []


def callback(in_data, frame_count, time_info, status):
    audio_queue.put(in_data)
    return (in_data, pyaudio.paContinue)

async def audio_stream(stop_event):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        stream_callback=callback)

    stream.start_stream()
    print("Recording...")

    try:
        while not stop_event.is_set():
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        print("Audio stream cancelled.")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("Audio stream closed.")

async def process_audio(stop_event, current_transcription_placeholder, processed_transcription_placeholder, save_interval, process_interval):
    try:
        frames = []
        last_save_time = time.time()
        last_process_time = time.time()
        transcription_count = 0
        procces_candidates = []

        while not stop_event.is_set():
            if not audio_queue.empty():
                audio_chunk = audio_queue.get()
                frames.append(audio_chunk)
                print(f"Processing audio chunk of size {len(audio_chunk)} bytes")

                current_time = time.time()

                # Save audio and transcribe every SAVE_INTERVAL seconds
                if current_time - last_save_time >= save_interval:
                    # Save the audio to a file
                    with wave.open("audio_chunk.wav", "wb") as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames))

                    frames = []
                    print("Transcribing audio...")
                    try:
                        transcription = speech_to_text_groq("audio_chunk.wav", client)
                        transcriptions.append(transcription)
                        procces_candidates.append(transcription)
                        transcription = " ".join(transcriptions)
                        st.session_state.current_transcription = transcription
                        current_transcription_placeholder.text_area(
                            "Current Transcription:",
                            transcription,
                            height=100,
                            key=f"current_transcription_display_{transcription_count}"
                        )
                        transcription_count += 1
                    except Exception as e:
                        print("Error during transcription: {}".format(e))
                        traceback.print_exc()
                        st.session_state.current_transcription = f"Error during transcription: {e}"
                    last_save_time = current_time

                # Process transcription every PROCESS_INTERVAL seconds
                if current_time - last_process_time >= process_interval:
                    try:
                        full_transcription = " ".join(procces_candidates)
                        procces_candidates = []
                        processed_text = process_transcription(full_transcription, client)
                        proccesed_candidates.append(processed_text)
                        processed_text = "\n".join(proccesed_candidates)
                        st.session_state.processed_transcription = processed_text
                        processed_transcription_placeholder.text_area(
                            "Processed Text:",
                            processed_text,
                            height=100,
                            key=f"processed_transcription_display_{transcription_count}"
                        )
                    except Exception as e:
                        print("Error during processing transcription: {}".format(e))
                        traceback.print_exc()
                        st.session_state.processed_transcription = f"Error during processing transcription: {e}"
                    last_process_time = current_time

            await asyncio.sleep(0.1)

        print("Finished recording. Processing any remaining frames.")

        # Process any remaining frames after stopping
        if frames:
            with wave.open("audio_chunk.wav", "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            print("Transcribing remaining audio...")
            if os.path.getsize("audio_chunk.wav") > 0:
                try:
                    transcription = speech_to_text_groq("audio_chunk.wav", client)
                    transcriptions.append(transcription)
                    st.session_state.current_transcription = transcription
                    current_transcription_placeholder.text_area(
                        "Remaining Transcription:",
                        transcription,
                        height=100,
                        key=f"remaining_transcription_display_{transcription_count}"
                    )
                except Exception as e:
                    print("Error during transcription: {}".format(e))
                    traceback.print_exc()
                    st.session_state.current_transcription = f"Error during transcription: {e}"
            else:
                print("No audio recorded.")
                st.session_state.current_transcription = "No audio recorded."
    except asyncio.CancelledError:
        print("Processing audio task cancelled.")
        traceback.print_exc()
    finally:
        print("Processing task stopped.")

async def start_transcription(current_transcription_placeholder, processed_transcription_placeholder, save_interval, process_interval):
    print("Starting transcription...")
    st.session_state.stop_event = asyncio.Event()
    await asyncio.gather(
        audio_stream(st.session_state.stop_event),
        process_audio(st.session_state.stop_event, current_transcription_placeholder, processed_transcription_placeholder, save_interval, process_interval),
    )
    st.session_state.recording = True
    st.write("Recording started...")

async def stop_transcription():
    print("Stopping transcription...")
    st.session_state.recording = False
    st.session_state.stop_event.set()
    st.write("Recording stopped.")

def main():
    st.set_page_config(
        page_title="Sunva Speech Transcription",
        page_icon="🔊",
    )

    st.sidebar.title("Settings")
    save_interval = st.sidebar.slider("Save Interval (seconds)", min_value=1, max_value=60, value=5, step=1)
    process_interval = st.sidebar.slider("Process Interval (seconds)", min_value=1, max_value=120, value=30, step=1)

    st.title("Sunva Speech Transcription")
    st.write("Click the buttons to start and stop real-time transcription.")

    # Initialize session state if not already done
    if 'recording' not in st.session_state:
        st.session_state.recording = False

    # Layout setup
    col1, col2 = st.columns([1, 3])

    with col1:
        start_button = st.button("Start Transcription", key="start_button")
        stop_button = st.button("Stop Transcription", key="stop_button")

    with col2:
        current_transcription_placeholder = st.empty()
        processed_transcription_placeholder = st.empty()

    if start_button and not st.session_state.recording:
        asyncio.run(start_transcription(current_transcription_placeholder, processed_transcription_placeholder, save_interval, process_interval))

    if stop_button and st.session_state.recording:
        asyncio.run(stop_transcription())

    if 'current_transcription' in st.session_state:
        current_transcription_placeholder.text_area(
            "Current Transcription:",
            st.session_state.current_transcription,
            height=100,
            key="current_transcription_display_initial"
        )

    if 'processed_transcription' in st.session_state:
        processed_transcription_placeholder.text_area(
            "Processed Text:",
            st.session_state.processed_transcription,
            height=100,
            key="processed_transcription_display_initial"
        )


if __name__ == "__main__":
    main()