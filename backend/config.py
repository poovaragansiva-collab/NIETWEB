from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    db_name: str = "college_tms"
    college_name: str = "ABC Engineering College"
    college_logo_path: str = "backend/static/college_logo.png"

    class Config:
        env_file = ".env"


settings = Settings()
