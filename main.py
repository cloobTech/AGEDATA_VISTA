from utils.email_service import send_email
from storage import DBStorage as DB
import asyncio


db = DB()


async def reload_db():
    """reload"""
    await db.drop_all()
    await db.reload()
    print('DB reloaded')

asyncio.run(reload_db())

