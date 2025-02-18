from typing import AsyncGenerator
from storage import db
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get DB Instance"""
    async for session in db.get_session():
        yield session
