from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True

    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"

    hf_api_key: str = ""
    image_provider: str = "mock"
    image_model: str = "black-forest-labs/FLUX.1-schnell"

    panel_count: int = Field(default=5, ge=1, le=10)
    image_width: int = Field(default=768, ge=256, le=1536)
    image_height: int = Field(default=768, ge=256, le=1536)

    static_dir: Path = BASE_DIR / "static"
    templates_dir: Path = BASE_DIR / "templates"
    panels_dir: Path = BASE_DIR / "static" / "panels"
    exports_dir: Path = BASE_DIR / "static" / "exports"
    generated_dir: Path = BASE_DIR / "static" / "generated"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    def create_directories(self) -> None:
        for directory in (
            self.static_dir,
            self.panels_dir,
            self.exports_dir,
            self.generated_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.create_directories()
    return settings
