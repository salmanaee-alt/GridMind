from pydantic import BaseModel


class Settings(BaseModel):
    project_name: str = "GridMind AI"


settings = Settings()