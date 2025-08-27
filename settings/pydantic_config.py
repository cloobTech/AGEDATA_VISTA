from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEV_ENV: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    EMAIL_CONFIG_USERNAME: str
    EMAIL_CONFIG_PASSWORD: str
    DATABASE_URL: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    FRONTEND_URL: str
    GROQ_API_KEY: str
    SUPABASE_KEY: str
    SUPABASE_URL: str
    PORT: int = 8000
    UV_COMPILE_BYTECODE: int
    UV_LINK_MODE: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )


# Load the settings
settings = Settings()
