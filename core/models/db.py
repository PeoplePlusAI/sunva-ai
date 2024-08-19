from sqlmodel import SQLModel, Field, select
from typing import Optional

# Define the transcription database model
class TranscriptionDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    transcription: str
    processed_text: Optional[str] = None
    word_count: int = 0  # Adding word_count to the model