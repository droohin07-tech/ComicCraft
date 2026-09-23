from __future__ import annotations

import re
import uuid
from pathlib import Path

from huggingface_hub import InferenceClient

from app.config import settings


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"

PANELS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# HUGGING FACE CLIENT
# ============================================================

_client = None


def get_client() -> InferenceClient:
    """
    Create the Hugging Face client only when it is needed.
    """

    global _client

    if _client is None:

        if not settings.hf_token:
            raise RuntimeError(
                "HF_TOKEN is missing from your .env file."
            )

        _client = InferenceClient(
            provider=settings.hf_provider,
            api_key=settings.hf_token,
        )

    return _client


# ============================================================
# FILENAME HELPER
# ============================================================

def _safe_filename(text: str) -> str:
    """
    Convert an arbitrary prompt into a safe filename.
    """

    text = str(text)

    text = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        text,
    )

    text = text.strip("_")

    if not text:
        text = "panel"

    return text[:60]


# ============================================================
# IMAGE GENERATION
# ============================================================

def generate_image(prompt: str) -> str:
    """
    Generate one comic panel image using Hugging Face.

    Returns:
        /static/panels/<filename>.png
    """

    if not prompt or not prompt.strip():
        raise ValueError(
            "Image generation prompt cannot be empty."
        )

    client = get_client()

    # Strengthen the prompt so the generated image
    # is appropriate for the ComicCraft workflow.
    final_prompt = f"""
Create a high-quality comic book illustration.

{prompt}

Visual requirements:
- clear subject
- strong composition
- expressive characters
- detailed environment
- cinematic lighting
- coherent perspective
- clean artwork
- no text
- no speech bubbles
- no captions
- no watermark
- maintain a consistent comic illustration style
""".strip()

    print()
    print("=" * 70)
    print("GENERATING COMIC PANEL IMAGE")
    print("=" * 70)
    print(final_prompt)
    print("=" * 70)

    try:

        image = client.text_to_image(
            prompt=final_prompt,
            model=settings.hf_image_model,
            width=settings.image_width,
            height=settings.image_height,
        )

    except Exception as exc:

        raise RuntimeError(
            f"Hugging Face image generation failed: {exc}"
        ) from exc

    if image is None:
        raise RuntimeError(
            "Hugging Face returned no image."
        )

    # ========================================================
    # SAVE IMAGE
    # ========================================================

    filename = (
        f"{_safe_filename(prompt)}_"
        f"{uuid.uuid4().hex[:8]}.png"
    )

    output_path = PANELS_DIR / filename

    try:

        image.save(output_path)

    except Exception as exc:

        raise RuntimeError(
            f"Could not save generated image: {exc}"
        ) from exc

    print(f"Image saved: {output_path}")
    print()

    # Browser-accessible URL
    return f"/static/panels/{filename}"