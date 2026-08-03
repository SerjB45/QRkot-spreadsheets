from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд QRKot'
    description: str = 'Благотворительный фонд поддержки котиков QRKot'
    database_url: str | None = 'sqlite+aiosqlite:///./charity_projects.db'
    secret: str = 'SECRET'
    yandex_disk_token: Optional[str] = None
    report_format: str = '%d.%m.%Y'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
