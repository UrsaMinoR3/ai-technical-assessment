from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: str = "changeme"
    azure_openai_key: str
    azure_openai_base_url: str
    azure_openai_model: str = "gpt-5.4-mini"
    deepgram_api_key: str
    database_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
