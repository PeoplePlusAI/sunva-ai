from sqlmodel import SQLModel, Field, Relationship, select
from typing import Optional, List

# Define the User database model
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password_hash: str

    # Relationships
    transcriptions: List["TranscriptionDB"] = Relationship(back_populates="user")
    speeches: List["SpeechDB"] = Relationship(back_populates="user")

# Define the Transcription database model
class TranscriptionDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    transcription: str
    processed_text: Optional[str] = None
    word_count: int = 0  # Adding word_count to the model
    language: str

    # Relationships
    user: Optional[User] = Relationship(back_populates="transcriptions")

# Define the Speech database model
class SpeechDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    audio: bytes
    text: Optional[str] = None
    language: str

    # Relationships
    user: Optional[User] = Relationship(back_populates="speeches")