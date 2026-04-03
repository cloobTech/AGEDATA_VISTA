from storage.database import DBStorage
from models import *
from settings.pydantic_config import settings


db = DBStorage(settings.DATABASE_URL)
