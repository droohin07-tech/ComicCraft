from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    environment: str = "development"

    host: str = "127.0.0.1"
    port: int = 8000

    # Gemini
    gemini_api_key: str = ""
    gemini_text_model: str = "gemini-2.5-flash"

    # Hugging Face
    hf_token: str = ""
    hf_image_model: str = (
        "stabilityai/stable-diffusion-3-medium-diffusers"
    )
    hf_provider: str = "hf-inference"

    # Image settings
    image_width: int = 768
    image_height: int = 512
    image_steps: int = 28

    # Directories
    output_dir: Path = BASE_DIR / "static"
    templates_dir: Path = BASE_DIR / "templates"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def panels_dir(self) -> Path:
        return self.output_dir / "panels"

    @property
    def exports_dir(self) -> Path:
        return self.output_dir / "exports"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    settings.panels_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    settings.exports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return settings