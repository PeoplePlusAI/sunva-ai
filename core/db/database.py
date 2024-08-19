from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

DATABASE_URL = "sqlite+aiosqlite:///./transcriptions.db"  # Replace with your DB URL

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

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