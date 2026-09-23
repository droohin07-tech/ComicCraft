from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# APPLICATION SETTINGS
# ============================================================

class Settings(BaseSettings):

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    app_name: str = "ComicCraft"
    app_version: str = "1.0.0"
    app_description: str = (
        "AI Comic Story Creator using Gemini and Hugging Face"
    )

    debug: bool = True

    # --------------------------------------------------------
    # Gemini
    # --------------------------------------------------------

    gemini_api_key: str = ""

    gemini_text_model: str = "gemini-3.5-flash-lite"

    # --------------------------------------------------------
    # Hugging Face
    # --------------------------------------------------------

    hf_token: str = ""

    hf_image_model: str = (
        "stabilityai/stable-diffusion-3-medium-diffusers"
    )

    hf_provider: str = "hf-inference"

    # --------------------------------------------------------
    # Image generation
    # --------------------------------------------------------

    image_width: int = 768
    image_height: int = 512
    image_steps: int = 28

    # --------------------------------------------------------
    # Comic settings
    # --------------------------------------------------------

    comic_panel_count: int = 5

    # --------------------------------------------------------
    # Server
    # --------------------------------------------------------

    host: str = "127.0.0.1"
    port: int = 8000

    # --------------------------------------------------------
    # Pydantic settings configuration
    # --------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ========================================================
    # PATHS
    # ========================================================

    @property
    def output_dir(self) -> Path:
        return BASE_DIR / "static"

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "static"

    @property
    def panels_dir(self) -> Path:
        return BASE_DIR / "static" / "panels"

    @property
    def exports_dir(self) -> Path:
        return BASE_DIR / "static" / "exports"

    @property
    def templates_dir(self) -> Path:
        return BASE_DIR / "templates"


# ============================================================
# SETTINGS SINGLETON
# ============================================================

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()