from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Telegram
    telegram_bot_token: SecretStr | None = None

    # Google Sheets
    google_service_account_json: SecretStr | None = None  # inline JSON string
    google_spreadsheet_id: str | None = None
    google_worksheet_name: str = "Expenses"


settings = Settings()
