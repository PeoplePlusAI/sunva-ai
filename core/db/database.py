from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from dotenv import load_dotenv
import os
import asyncpg
import sqlalchemy as sa
import time
from sqlalchemy.exc import SQLAlchemyError

from asyncpg.exceptions import DuplicatePreparedStatementError

load_dotenv(
        "ops/.env"
        )

DATABASE_URL = os.getenv("DATABASE_URL")
#DATABASE_URL = os.getenv("DATABASE_URL") + "?prepared_statement_cache_size=0"


# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
#engine = create_async_engine(DATABASE_URL, echo=True, future=True, pool_size=5, max_overflow=10, connect_args={"statement_cache_size": 0}                     )

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



# Function to initialize the database (creating tables)
async def init_db(retry_attempts=10):
    attempt = 0
    retry_delay = 5
    retry_attempts = 10
    while attempt < retry_attempts:
        try:
            async with engine.begin() as conn:
                # Optionally drop all tables for a fresh start
                await conn.run_sync(SQLModel.metadata.drop_all)
                # Create all tables
                await conn.run_sync(SQLModel.metadata.create_all)
            print("Database initialization successful.")
            break
        except (DuplicatePreparedStatementError, SQLAlchemyError) as e:  # Catch specific exceptions
            print(f"Database initialization failed due to {type(e).__name__}: {e}. Retrying in {retry_delay} seconds...")
            attempt += 1
            if attempt < retry_attempts:
                time.sleep(retry_delay)  # Delay before the next retry
            else:
                print("Max retries reached. Exiting...")
                raise  # Re-raise after max retries

# Dependency to get a session
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Graceful shutdown: Dispose engine on app shutdown
async def shutdown():
    await engine.dispose()

