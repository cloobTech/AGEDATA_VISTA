import uvicorn
from settings.pydantic_config import settings


if __name__ == "__main__":
    uvicorn.run("api.v1.main:app", host="0.0.0.0",
                port=settings.PORT, reload=True)
