import streamlit as st
import numpy as np
import sounddevice as sd
import soundfile as sf
import os
from groq import Groq
from TTS.api import TTS
from faster_whisper import WhisperModel
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Groq 
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# TTS and WhisperModel
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8",
    cpu_threads=int(os.cpu_count() / 2),
)

# prompts
with open("../prompts/concise.txt", "r") as f:
    concise_prompt = f.read()

with open("../prompts/highlight.txt", "r") as f:
    highlight_prompt = f.read()

with open("../prompts/decision.txt", "r") as f:
    decision_prompt = f.read()

with open("../prompts/correction.txt", "r") as f:
    correction_prompt = f.read()

def speech_to_text(audio_chunk, model):
    segments, info = model.transcribe(
        audio_chunk, beam_size=5, language="en"
    )
    speech_text = " ".join(
        [
            segment.text for segment in segments
        ]
    )
    return speech_text

def concise_transcription(transcription: str, client: Groq) -> str:
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "system",
                "content": concise_prompt.format(transcription)
            }
        ]
    )
    return chat_completion.choices[0].message.content

def highlight_keywords(transcription: str, client: Groq) -> str:
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "system",
                "content": highlight_prompt.format(transcription)
            }
        ]
    )
    return chat_completion.choices[0].message.content

def should_summarize(transcription: str, client: Groq) -> bool:
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "system",
                "content": decision_prompt.format(transcription)
            }
        ]
    )
    response = chat_completion.choices[0].message.content
    return response.lower() == "yes"

def correct_transcription(transcription: str, client: Groq) -> str:
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "system",
                "content": correction_prompt.format(transcription)
            }
        ]
    )
    return chat_completion.choices[0].message.content

def process_transcription(transcription: str, client: Groq) -> str:
    if should_summarize(transcription, client):
        return concise_transcription(transcription, client)
    else:
        return highlight_keywords(transcription, client)

def record_audio(duration: float, fs: int) -> np.ndarray:
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    return recording.flatten()

def save_wav(audio_data: np.ndarray, fs: int, file_name: str):
    sf.write(file_name, audio_data, fs)

def save_transcription(text: str, file_name: str):
    with open(file_name, "w") as f:
        f.write(text)

def play_audio(audio_data: np.ndarray, fs: int):
    sd.play(audio_data, fs)
    sd.wait()

def load_audio_history():
    if os.path.exists("audio_history.json"):
        with open("audio_history.json", "r") as f:
            return json.load(f)
    else:
        return []

def save_audio_history(audio_history):
    with open("audio_history.json", "w") as f:
        json.dump(audio_history, f)

def load_audio(file_name):
    audio_data, fs = sf.read(file_name)
    return audio_data, fs

# app
def main():
    st.set_page_config(layout="wide")
    st.title("Audio Transcription for Deaf People")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Record or Upload Audio")
        record_stop_button = st.button("Start/Stop Recording")
        recording_duration = st.number_input("Recording duration (seconds)", min_value=1.0, step=1.0, value=5.0)
        uploaded_file = st.file_uploader("Or upload an audio file (wav format)", type=["wav"], key="audio_file")

    fs = 16000  # Sample rate
    audio_data = None
    recording_in_progress = False
    audio_history = load_audio_history()

    if record_stop_button:
        if not recording_in_progress:
            audio_data = record_audio(recording_duration, fs)
            recording_in_progress = True
            st.session_state.file_uploaded = False
        else:
            file_name = "recorded_audio.wav"
            save_wav(audio_data, fs, file_name)
            audio_history.append({
                "filename": file_name,
                "transcription": speech_to_text(file_name, model)
            })
            save_audio_history(audio_history)

            audio_data = None
            recording_in_progress = False
            st.session_state.file_uploaded = False

    if uploaded_file:
        # Process uploaded audio file
        audio_data, fs = sf.read(uploaded_file)
        file_name = f"uploaded_{uploaded_file.name}"
        save_wav(audio_data, fs, file_name)
        audio_history.append({
            "filename": file_name,
            "transcription": speech_to_text(file_name, model)
        })
        save_audio_history(audio_history)

        st.session_state.file_uploaded = True

    with col2:
        st.header("Audio History and Transcriptions")
        for i, entry in enumerate(audio_history):
            with st.expander(f"Audio {i+1}: {entry['filename']}"):
                if st.button(f"Play Audio {i+1}", key=f"play_{i}"):
                    audio_data, fs = load_audio(entry['filename'])
                    play_audio(audio_data, fs)
                st.markdown(
                    f"<div style='background-color: {['#ffa07a', '#87ceeb', '#90ee90', '#ffb6c1'][i%4]};padding:10px;border-radius:10px;margin-bottom:10px;color:black;'>{process_transcription(entry['transcription'], client)}</div>",
                    unsafe_allow_html=True,
                )

if __name__ == "__main__":
    if "file_uploaded" not in st.session_state:
        st.session_state.file_uploaded = False
    main()