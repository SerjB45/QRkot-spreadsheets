from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд QRKot'
    description: str = 'Благотворительный фонд поддержки котиков QRKot'
    database_url: str | None = 'sqlite+aiosqlite:///./charity_projects.db'
    secret: str = 'SECRET'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
