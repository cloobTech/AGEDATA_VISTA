from typing import AsyncGenerator
from storage import db
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes"""
    async with db.get_session() as session:
        yield session
