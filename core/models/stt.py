from pydantic import BaseModel

class Transcription(BaseModel):
    id: int
    transcription: str

class ProcessedText(BaseModel):
    transcription: str
    processed_text: str

class TranscriptionResponse(BaseModel):
    transcriptions: list[Transcription]

class SingleTranscriptionResponse(BaseModel):
    transcription: Transcription

class WebSocketResponse(BaseModel):
    transcription: str = None
    processed_text: str = None
    original_text: str = None
    style: str = None