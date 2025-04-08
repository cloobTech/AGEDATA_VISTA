# from storage import DBStorage as DB
# import asyncio


# db = DB()


# async def reload_db():
#     """reload"""
#     await db.drop_all()
#     await db.reload()
#     print('DB reloaded')

# asyncio.run(reload_db())

import uvicorn
from settings.pydantic_config import settings


if __name__ == "__main__":
    uvicorn.run("api.v1.main:app", host="0.0.0.0", port=settings.PORT, reload=True)

