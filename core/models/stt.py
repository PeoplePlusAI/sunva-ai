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
    message_id: str
    text: str
    type: str