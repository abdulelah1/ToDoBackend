from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    ENCRYPTION_KEY: str
    ENCRYPTION_ALGO: str

    class Config:
        env_file = ".env"

    @property
    def database_url(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}"

# Create an instance of the Settings class
settings = Settings()

