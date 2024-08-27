from .database import engine
from sqlmodel import SQLModel
# from core.models.db import TranscriptionDB

# Initialize the database by creating tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)