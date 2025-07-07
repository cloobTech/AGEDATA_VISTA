import uvicorn
import subprocess
from settings.pydantic_config import settings

if __name__ == "__main__":
    if settings.DEV_ENV == "production":
        # Runs: alembic upgrade head && gunicorn ...
        print("Running in production mode with Gunicorn...")

        # Run Alembic migrations first
        subprocess.run(["alembic", "upgrade", "head"], check=True)

        # Then run Gunicorn with Uvicorn worker
        subprocess.run([
            "gunicorn",
            "api.v1.main:app",
            "-k", "uvicorn.workers.UvicornWorker",
            "--bind", f"0.0.0.0:{settings.PORT}"
        ], check=True)

    else:
        # Run Alembic migrations first
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        # Dev mode: hot-reload server with uvicorn directly
        uvicorn.run(
            "api.v1.main:app",
            host="0.0.0.0",
            port=settings.PORT,
            reload=True
        )
