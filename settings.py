from pydantic import BaseSettings

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    secret_key: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    cloudinary_cloud_name: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()