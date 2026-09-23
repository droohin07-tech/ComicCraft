from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import (
    ComicOutline,
    ComicStory,
    PromptRequest,
)


class GeminiService:

    def __init__(self) -> None:
        self.settings = get_settings()

        if not self.settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file."
            )

        self.client = genai.Client(
            api_key=self.settings.gemini_api_key
        )

    def _generate_json(
        self,
        prompt: str,
        schema: type
    ):
        response = self.client.models.generate_content(
            model=self.settings.gemini_text_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.9,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return schema.model_validate_json(
            response.text
        )

    def generate_outline(
        self,
        request: PromptRequest
    ) -> ComicOutline:

        prompt = f"""
Create a coherent five-panel comic outline.

User story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:

- Exactly 5 panels.
- Preserve the user's character.
- Preserve the requested setting.
- Preserve the requested tone.
- The story must progress logically from panel 1 to panel 5.
- Every panel needs a clear visual scene.
- Every panel needs an image-generation prompt.
- Keep the protagonist visually consistent.
- Describe clothing, appearance, environment and action
  whenever useful.
- Do not place dialogue or text inside the generated images.
- Do not add logos or watermarks.
"""

        return self._generate_json(
            prompt,
            ComicOutline
        )

    def generate_story(
        self,
        request: PromptRequest,
        outline: ComicOutline
    ) -> ComicStory:

        outline_text = outline.model_dump_json(
            indent=2
        )

        prompt = f"""
Write the final five-panel comic script
from the following outline.

Character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Original story:
{request.story_prompt}

Outline:
{outline_text}

Requirements:

- Exactly 5 story objects.
- Panel numbers must match the outline.
- Each panel gets a short caption.
- Each panel gets narration.
- Each panel may have dialogue.
- Dialogue must feel natural.
- Maintain continuity.
- Do not change the protagonist.
- Do not change the setting without narrative reason.
- Keep each panel concise enough for a comic.
"""

        return self._generate_json(
            prompt,
            ComicStory
        )