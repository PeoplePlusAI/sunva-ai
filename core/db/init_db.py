from .database import engine
from sqlmodel import SQLModel
# from core.models.db import TranscriptionDB


SQLModel.metadata.bind = engine

# Initialize the database by creating tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def shutdown_db():
   await engine.dispose()