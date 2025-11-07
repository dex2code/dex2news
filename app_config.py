from pydantic import BaseModel, ConfigDict, Field, field_validator, SecretStr
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from tomllib import load as toml_load
from os import getenv as os_getenv
from wrappers import in_out_debug

class AppConfig(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='ignore'
    )

    app_name: str = Field(default="Nuntius Mutationum")
    app_version: str = Field(default="1.0.0")

    tg_bot_token: SecretStr = Field(default=SecretStr(secret_value=""), description="Telegram bot token")
    tg_chat_id: SecretStr = Field(default=SecretStr(secret_value=""), description="Telegram Chat ID to send the news")
    news_api_token: SecretStr = Field(default=SecretStr(secret_value=""), description="News API token")

    @field_validator('tg_bot_token')
    @classmethod
    def validate_bot_token(cls, value: str) -> str:
        if not value:
            raise ValueError("Telegram bot token is empty!")
        return value

    @field_validator('tg_chat_id')
    @classmethod
    def validate_chat_id(cls, value: str) -> str:
        if not value:
            raise ValueError("Telegram chat ID is empty!")
        return value

    @field_validator('news_api_token')
    @classmethod
    def validate_news_token(cls, value: str) -> str:
        if not value:
            raise ValueError(f"News API token is empty!")
        return value

    news_api_endpoint: str = Field(default="https://gnews.io/api/v4/top-headlines", description="GNews API endpoint")
    news_api_timeout_sec: int = Field(default=1, ge=1, description="News API timeout in seconds")
    news_lang: str = Field(default="ru", description="News language")
    news_categories: List[str] = Field(default=["general"], description="List of news categories")
    news_max_articles: int = Field(default=1, ge=1, description="How many topics to request from each category")
    news_delay_hours: int = Field(default=12, description="News datetime delay")
    news_period_hours: int = Field(default=3, description="Time period of news publication")

    log_path: Path = Field(default=Path('logs/main.log'), description="Path to log file including directory")
    log_level: str = Field(default="INFO", description="Logging level")
    log_enqueue: bool = Field(default=True, description="Enqueue logs for async")
    log_rotation: str = Field(default="1 day", description="How often rotate logs")
    log_retention: str = Field(default="1 month", description="Remove logs older than retention value")


@in_out_debug
def load_config(path: Path) -> AppConfig:
    if not load_dotenv():
        raise FileNotFoundError("Cannot load .env file! Check file or key values.")
    env_config = {
        'tg_bot_token': os_getenv(key='tg_bot_token'),
        'tg_chat_id': os_getenv(key='tg_chat_id'),
        'news_api_token': os_getenv(key='news_api_token')
    }

    try:
        with open(file=path, mode='rb') as f:
            toml_config = toml_load(f)
    except FileNotFoundError:
        toml_config = {}
    
    app_config = {**env_config, **toml_config}

    return AppConfig(**app_config)


app_config = load_config(
    Path('config.toml')
)


if __name__ == "__main__":
    pass