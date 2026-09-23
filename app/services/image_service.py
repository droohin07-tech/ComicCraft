from datetime import datetime

from huggingface_hub import InferenceClient

from app.config import get_settings


class ImageService:

    def __init__(self) -> None:
        self.settings = get_settings()

        if not self.settings.hf_token:
            raise RuntimeError(
                "HF_TOKEN is not configured. "
                "Add it to your .env file."
            )

        self.client = InferenceClient(
            provider=self.settings.hf_provider,
            api_key=self.settings.hf_token,
        )

    def generate_image(
        self,
        prompt: str,
        panel_number: int
    ) -> str:

        enhanced_prompt = f"""
{prompt}

Professional sequential comic illustration.
Strong readable composition.
Consistent character design.
Clean linework.
Cinematic lighting.
Detailed environment.
Dynamic composition.

Do NOT include:
- words
- letters
- captions
- speech bubbles
- logos
- watermarks
"""

        image = self.client.text_to_image(
            prompt=enhanced_prompt,
            model=self.settings.hf_image_model,
            width=self.settings.image_width,
            height=self.settings.image_height,
        )

        filename = (
            f"panel_{panel_number}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            f".png"
        )

        path = self.settings.panels_dir / filename

        image.save(path)

        return f"/static/panels/{filename}"


def generate_test_image(prompt: str) -> str:
    service = ImageService()

    return service.generate_image(
        prompt,
        0
    )