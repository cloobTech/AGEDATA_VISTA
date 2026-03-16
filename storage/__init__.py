from storage.database import DBStorage
from models import *
from settings.pydantic_config import settings


if settings.DEV_ENV == "production":
    db = DBStorage(settings.DATABASE_URL)
else:
    """ db = DBStorage(db_uri='sqlite+aiosqlite:///:memory:') """
    db = DBStorage(db_uri="sqlite+aiosqlite:///./test.db")
