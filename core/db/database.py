from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import sqlalchemy as sa

from dotenv import load_dotenv
import os
load_dotenv(
    "ops/.env"
)

DATABASE_URL = os.getenv("DATABASE_URL")

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True, poolclass=sa.NullPool,
                             connect_args={
                                 "prepared_statement_cache_size": 0,
                                 "statement_cache_size": 0
                                 }
                             )
# Create the async session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to get the async session
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
